def calculate_growth(initial_amount, annual_rate, monthly_contribution, years, compound=True):
    total_contributions = monthly_contribution * 12 * years
    monthly_rate = annual_rate / 12

    if monthly_rate == 0:
        # Handle zero monthly rate case separately
        total_amount = initial_amount + total_contributions
    else:
        if compound:
            total_amount = (
                initial_amount * (1 + monthly_rate) ** (12 * years) +
                monthly_contribution * (((1 + monthly_rate) ** (12 * years) - 1) / monthly_rate)
            )
        else:
            total_amount = (
                initial_amount +
                initial_amount * annual_rate * years +
                total_contributions
            )

    interest = total_amount - initial_amount - total_contributions
    balance = total_amount

    return interest, balance

def calculate_monthly_payment(total_debt, interest_rate, months):
    annual_rate = interest_rate / 100
    monthly_rate = annual_rate / 12

    if monthly_rate == 0:
        return total_debt / months
    else:
        monthly_payment = (total_debt * monthly_rate) / (1 - (1 + monthly_rate) ** -months)
        return round(monthly_payment, 2)

def calculate_debt_payoff(total_debt, interest_rate, monthly_payment):
    annual_rate = interest_rate / 100
    monthly_rate = annual_rate / 12

    if monthly_payment <= total_debt * monthly_rate:
        return None, None, None, None, None  # Payment is too low to cover interest

    months = 0
    remaining_debt = total_debt
    total_interest = 0

    payment_schedule = []
    graph_data = {
        'months': [0],
        'remaining_debt': [total_debt],
        'cumulative_interest': [0],
        'cumulative_principal': [0]
    }

    while remaining_debt > 0:
        interest = remaining_debt * monthly_rate
        principal = min(monthly_payment - interest, remaining_debt)
        
        total_interest += interest
        remaining_debt -= principal
        months += 1

        payment_schedule.append({
            'month': months,
            'payment': monthly_payment if remaining_debt > 0 else principal + interest,
            'principal': principal,
            'interest': interest,
            'remaining': max(remaining_debt, 0)
        })

        graph_data['months'].append(months)
        graph_data['remaining_debt'].append(max(remaining_debt, 0))
        graph_data['cumulative_interest'].append(total_interest)
        graph_data['cumulative_principal'].append(total_debt - remaining_debt)

        if months > 1200:  # To prevent infinite loop in case of errors
            break

    years = months // 12
    extra_months = months % 12

    return years, extra_months, total_interest, payment_schedule, graph_data

def calculate_retirement_savings(current_savings, monthly_contribution, annual_return, months):
    monthly_return = annual_return / 12
    future_value = current_savings * (1 + monthly_return) ** months
    future_value += monthly_contribution * ((1 + monthly_return) ** months - 1) / monthly_return
    return future_value

def calculate_required_savings(current_savings, target_savings, annual_return, months):
    monthly_return = annual_return / 12
    required_monthly_savings = (target_savings - current_savings * (1 + monthly_return) ** months) / (((1 + monthly_return) ** months - 1) / monthly_return)
    return required_monthly_savings

def calculate_retirement_savings_with_inflation(current_savings, monthly_contribution, annual_return, inflation_rate, years):
    monthly_return = annual_return / 12
    monthly_inflation = inflation_rate / 12
    yearly_data = []

    balance = current_savings
    inflation_adjusted_balance = current_savings
    total_contributions = 0

    for year in range(years + 1):
        if year > 0:
            for _ in range(12):
                balance += monthly_contribution
                balance *= (1 + monthly_return)
                total_contributions += monthly_contribution

            inflation_adjusted_balance = balance / ((1 + inflation_rate) ** year)

        yearly_data.append({
            'year': year,
            'balance': round(balance, 2),
            'inflation_adjusted_balance': round(inflation_adjusted_balance, 2),
            'total_contributions': round(total_contributions, 2)
        })

    return yearly_data