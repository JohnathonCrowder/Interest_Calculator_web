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

def calculate_debt_payoff(total_debt, interest_rate, monthly_payment):
    annual_rate = interest_rate / 100
    monthly_rate = annual_rate / 12

    if monthly_payment <= total_debt * monthly_rate:
        return None, None, None, None, None  # Payment is too low to cover interest

    months = 0
    remaining_debt = total_debt
    total_interest = 0
    total_principal = 0

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
        total_principal += principal
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
        graph_data['cumulative_principal'].append(total_principal)

        if months > 1200:  # To prevent infinite loop in case of errors
            break

    years = months // 12
    extra_months = months % 12

    return years, extra_months, total_interest, payment_schedule, graph_data