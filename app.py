from flask import Flask, render_template, request
from calculations import calculate_growth

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

if __name__ == '__main__':
    app.run(debug=True)