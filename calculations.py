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