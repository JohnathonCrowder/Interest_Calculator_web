from flask import Flask, render_template, request, jsonify
from calculations import calculate_growth, calculate_debt_payoff, calculate_monthly_payment
from calculations import calculate_retirement_savings, calculate_required_savings
import datetime

from calculations import calculate_retirement_savings_with_inflation
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data from the request
        rate = float(request.form.get('rate', 0))
        initial_amount = float(request.form.get('initial_amount', 0))
        monthly_contribution = float(request.form.get('monthly_contribution', 0))
        compound = request.form.get('compound', 'on') == 'on'

        if rate == 0:
            # Handle zero interest rate case
            years = [0, 1] + [5 * i for i in range(1, 5)]
            balances = [initial_amount] * len(years)
            interest_amounts = [0] * len(years)
            principal_amounts = [initial_amount + monthly_contribution * 12 * year for year in years]
        else:
            # Perform calculations
            years = [0, 1] + [5 * i for i in range(1, 5)]
            balances = []
            interest_amounts = []
            principal_amounts = []
            total_contributions = 0

            # Calculate initial balance and interest for year 0
            balances.append(initial_amount)
            interest_amounts.append(0)
            principal_amounts.append(initial_amount)

            # Add year 1 balance
            interest, balance = calculate_growth(initial_amount, rate / 100, monthly_contribution, 1, compound)
            balances.append(balance)
            interest_amounts.append(interest)
            principal_amounts.append(initial_amount + monthly_contribution * 12)

            # Update GUI with long-term results (5, 10, 15, 20 years)
            for year in years[2:]:
                interest, balance = calculate_growth(initial_amount, rate / 100, monthly_contribution, year, compound)
                balances.append(balance)
                interest_amounts.append(interest)
                total_contributions += monthly_contribution * 12 * (year - years[years.index(year) - 1])
                principal_amounts.append(initial_amount + total_contributions)

        # Generate the plot data
        plot_data = generate_plot(years, balances, interest_amounts, principal_amounts)

        # Render the template with the calculation results and plot data
        return render_template('index.html', data=list(zip(years, balances, interest_amounts, principal_amounts)),
                               plot_data=plot_data, rate=rate, initial_amount=initial_amount,
                               monthly_contribution=monthly_contribution, compound=compound)

    # Render the template for the initial GET request
    return render_template('index.html')

@app.route('/debt-calculator', methods=['GET', 'POST'])
def debt_calculator():
    total_debt = 0
    interest_rate = 0
    monthly_payment = 0
    years = None
    extra_months = None
    total_interest = None
    payment_schedule = None
    plot_data = None

    if request.method == 'POST':
        total_debt = float(request.form.get('total_debt', 0))
        interest_rate = float(request.form.get('interest_rate', 0))
        monthly_payment = float(request.form.get('monthly_payment', 0))

        years, extra_months, total_interest, payment_schedule, graph_data = calculate_debt_payoff(total_debt, interest_rate, monthly_payment)
        if graph_data:
            plot_data = generate_debt_plot(graph_data)

    return render_template('debt_calculator.html', 
                          total_debt=total_debt,
                          interest_rate=interest_rate,
                          monthly_payment=monthly_payment,
                          years=years,
                          extra_months=extra_months,
                          total_interest=total_interest,
                          payment_schedule=payment_schedule,
                          plot_data=plot_data)

@app.route('/calculate-debt', methods=['POST'])
def calculate_debt():
    total_debt = float(request.form.get('total_debt', 0))
    interest_rate = float(request.form.get('interest_rate', 0))
    monthly_payment = float(request.form.get('monthly_payment', 0))

    years, extra_months, total_interest, payment_schedule, graph_data = calculate_debt_payoff(total_debt, interest_rate, monthly_payment)
    plot_data = {
        'months': graph_data['months'],
        'remaining_debt': graph_data['remaining_debt'],
        'cumulative_interest': graph_data['cumulative_interest'],
        'cumulative_principal': graph_data['cumulative_principal']
    }

    return jsonify({
        'years': years,
        'extra_months': extra_months,
        'total_interest': total_interest,
        'payment_schedule': payment_schedule,
        'plot_data': plot_data
    })

@app.route('/retirement-calculator')
def retirement_calculator():
    return render_template('retirement_calculator.html')

@app.route('/calculate-retirement', methods=['POST'])
def calculate_retirement():
    current_age = int(request.form.get('current_age'))
    retirement_age = int(request.form.get('retirement_age'))
    current_savings = float(request.form.get('current_savings'))
    monthly_contribution = float(request.form.get('monthly_contribution'))
    expected_return = float(request.form.get('expected_return')) / 100
    inflation_rate = float(request.form.get('inflation_rate')) / 100

    years_until_retirement = retirement_age - current_age

    yearly_data = calculate_retirement_savings_with_inflation(
        current_savings, monthly_contribution, expected_return, inflation_rate, years_until_retirement
    )

    return jsonify({
        'projected_savings': round(yearly_data[-1]['balance'], 2),
        'inflation_adjusted_savings': round(yearly_data[-1]['inflation_adjusted_balance'], 2),
        'total_contributions': round(yearly_data[-1]['total_contributions'], 2),
        'total_interest': round(yearly_data[-1]['balance'] - yearly_data[-1]['total_contributions'], 2),
        'yearly_data': yearly_data
    })

@app.route('/calculate-monthly-payment', methods=['POST'])
def calculate_monthly_payment_route():
    data = request.get_json()
    total_debt = float(data.get('total_debt', 0))
    interest_rate = float(data.get('interest_rate', 0))
    target_date_str = data.get('target_date')

    if not total_debt or not interest_rate or not target_date_str:
        return jsonify({'error': 'Invalid input data'})

    try:
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'})

    today = datetime.date.today()
    if target_date <= today:
        return jsonify({'error': 'Target date must be in the future'})

    months = (target_date.year - today.year) * 12 + target_date.month - today.month
    monthly_payment = calculate_monthly_payment(total_debt, interest_rate, months)

    return jsonify({'monthly_payment': monthly_payment})


def generate_plot(years, balances, interest_amounts, principal_amounts):
    # Create a new figure and axes
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100, tight_layout=True)

    # Plot the total balance line
    ax.plot(years, balances, marker='o', label='Total Balance', color='#3498db', linewidth=2)

    # Plot the accumulated interest line
    ax.plot(years, interest_amounts, marker='o', label='Accumulated Interest', color='#e74c3c', linewidth=2)

    # Fill the area between total balance and principal to show interest
    ax.fill_between(years, principal_amounts, balances, color='#e74c3c', alpha=0.3, label='Interest Area')

    # Fill the area below principal to show contributions
    ax.fill_between(years, 0, principal_amounts, color='#2ecc71', alpha=0.3, label='Principal + Contributions')

    # Set labels and title
    ax.set_xlabel('Years', fontsize=10)
    ax.set_ylabel('Amount ($)', fontsize=10)
    ax.set_title('Account Balance and Interest Growth', fontsize=12, fontweight='bold')

    # Customize the plot
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Format y-axis labels to display in dollars
    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
    )

    # Add a legend
    ax.legend(loc='upper left', fontsize=8, framealpha=0.6, edgecolor='none')

    # Set the y-axis to start from 0
    ax.set_ylim(bottom=0)

    # Save the plot to a temporary buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the plot as a base64 string
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return plot_data

def generate_debt_plot(graph_data):
    months = graph_data['months']
    remaining_debt = graph_data['remaining_debt']
    cumulative_interest = graph_data['cumulative_interest']
    cumulative_principal = graph_data['cumulative_principal']

    fig, ax = plt.subplots(figsize=(8, 6), dpi=100, tight_layout=True)

    ax.plot(months, remaining_debt, marker='o', label='Remaining Debt', color='#e74c3c', linewidth=2)
    ax.plot(months, cumulative_interest, marker='o', label='Cumulative Interest', color='#f39c12', linewidth=2)
    ax.plot(months, cumulative_principal, marker='o', label='Cumulative Principal', color='#2ecc71', linewidth=2)

    ax.fill_between(months, 0, cumulative_principal, color='#2ecc71', alpha=0.3, label='Principal Area')
    ax.fill_between(months, cumulative_principal, [a + b for a, b in zip(cumulative_principal, cumulative_interest)], color='#f39c12', alpha=0.3, label='Interest Area')

    ax.set_xlabel('Months', fontsize=10)
    ax.set_ylabel('Amount ($)', fontsize=10)
    ax.set_title('Debt Repayment Over Time', fontsize=12, fontweight='bold')

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=8)

    ax.get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: f'${x:,.0f}')
    )

    ax.legend(loc='upper right', fontsize=8, framealpha=0.6, edgecolor='none')
    ax.set_ylim(bottom=0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    return plot_data

if __name__ == '__main__':
    app.run(debug=True)