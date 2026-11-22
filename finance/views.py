from .scam_detector import detect_scam
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    Transaction,
    Budget,
    ScamDetectionHistory,
    SavingsGoal
)
from .forms import TransactionForm, BudgetForm
def home(request):
    return render(request, 'finance/index.html')
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'finance/register.html', {'form': form})
def user_login(request):
    from django.contrib.auth.forms import AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'finance/login.html', {'form': form})
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')
@login_required
def dashboard(request):
    user_transactions = Transaction.objects.filter(
        user=request.user
    )
    recent_transactions = user_transactions.order_by(
        '-date', '-id'
    )[:5]
    total_income = user_transactions.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = user_transactions.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance = total_income - total_expenses
    if total_income > 0:
        savings_rate = float(
            (balance / total_income) * Decimal('100')
        )
    else:
        savings_rate = 0
    today = timezone.localdate()
    current_month = today.strftime('%Y-%m')
    current_month_transactions = user_transactions.filter(
        date__year=today.year,
        date__month=today.month
    )
    current_month_expenses = (
        current_month_transactions.filter(
            transaction_type='Expense'
        ).aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    monthly_budget = Budget.objects.filter(
        user=request.user,
        month=current_month
    ).first()
    budget_amount = (
        monthly_budget.amount
        if monthly_budget else Decimal('0.00')
    )
    if budget_amount > 0:
        budget_percentage = float(
            (current_month_expenses / budget_amount)
            * Decimal('100')
        )
    else:
        budget_percentage = 0
    budget_progress = min(budget_percentage, 100)
    if total_income > 0:
        if savings_rate >= 20:
            savings_score = 30
        elif savings_rate >= 10:
            savings_score = 20
        elif savings_rate > 0:
            savings_score = 10
        else:
            savings_score = 0
        expense_ratio = (
            total_expenses / total_income
        ) * Decimal('100')
        if expense_ratio <= 50:
            expense_score = 30
        elif expense_ratio <= 70:
            expense_score = 20
        elif expense_ratio <= 90:
            expense_score = 10
        else:
            expense_score = 0
        income_score = 20 if total_expenses < total_income else (
            10 if total_expenses == total_income else 0
        )
    else:
        savings_score = 0
        expense_score = 0
        income_score = 0
    if budget_amount <= 0:
        budget_score = 0
    elif budget_percentage <= 50:
        budget_score = 20
    elif budget_percentage <= 75:
        budget_score = 15
    elif budget_percentage <= 90:
        budget_score = 10
    elif budget_percentage <= 100:
        budget_score = 5
    else:
        budget_score = 0
    financial_health_score = (
        savings_score
        + expense_score
        + budget_score
        + income_score
    )
    category_data = user_transactions.filter(
        transaction_type='Expense'
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    chart_labels = [
        item['category'] for item in category_data
    ]
    chart_values = [
        float(item['total']) for item in category_data
    ]
    monthly_data = user_transactions.filter(
        transaction_type='Expense'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    month_labels = [
        item['month'].strftime('%b %Y')
        for item in monthly_data
    ]
    month_values = [
        float(item['total'])
        for item in monthly_data
    ]
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'savings_rate': round(savings_rate, 1),
        'budget_amount': budget_amount,
        'current_month_expenses': current_month_expenses,
        'budget_percentage': round(budget_percentage, 1),
        'budget_progress': budget_progress,
        'financial_health_score': financial_health_score,
        'recent_transactions': recent_transactions,
        'chart_summary': [
            float(total_income),
            float(total_expenses)
        ],
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'month_labels': month_labels,
        'month_values': month_values,
    }
    return render(
        request,
        'finance/dashboard.html',
        context
    )
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transactions')
    else:
        form = TransactionForm()
    return render(
        request,
        'finance/add_transaction.html',
        {'form': form}
    )
@login_required
def transactions(request):
    records = Transaction.objects.filter(
        user=request.user
    )
    search_query = request.GET.get('search', '').strip()
    if search_query:
        records = records.filter(
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    selected_type = request.GET.get('type', '').strip()
    if selected_type in ['Income', 'Expense']:
        records = records.filter(
            transaction_type=selected_type
        )
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    filter_error = ''
    try:
        parsed_start = (
            date.fromisoformat(start_date)
            if start_date else None
        )
        parsed_end = (
            date.fromisoformat(end_date)
            if end_date else None
        )
        if parsed_start and parsed_end and parsed_start > parsed_end:
            filter_error = 'Start date cannot be after end date.'
        else:
            if parsed_start:
                records = records.filter(date__gte=parsed_start)

            if parsed_end:
                records = records.filter(date__lte=parsed_end)
    except ValueError:
        filter_error = 'Please enter valid dates.'
        records = Transaction.objects.filter(user=request.user)
    records = records.order_by('-date', '-created_at')
    context = {
        'records': records,
        'search_query': search_query,
        'selected_type': selected_type,
        'start_date': start_date,
        'end_date': end_date,
        'filter_error': filter_error,
    }
    return render(
        request,
        'finance/transactions.html',
        context
    )
@login_required
def delete_transaction(request, pk):
    if request.method == 'POST':
        record = get_object_or_404(
            Transaction,
            pk=pk,
            user=request.user
        )
        record.delete()
    return redirect('transactions')
@login_required
def edit_transaction(request, pk):
    record = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )
    if request.method == 'POST':
        form = TransactionForm(
            request.POST,
            instance=record
        )
        if form.is_valid():
            form.save()
            return redirect('transactions')
    else:
        form = TransactionForm(instance=record)
    return render(
        request,
        'finance/add_transaction.html',
        {'form': form, 'edit_mode': True}
    )
@login_required
def ai_insights(request):
    expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='Expense'
    )
    income = Transaction.objects.filter(
        user=request.user,
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_expenses = expenses.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    balance = income - total_expenses
    category_data = expenses.values(
        'category'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')
    highest_category = None
    highest_amount = Decimal('0.00')
    if category_data.exists():
        highest_category = category_data[0]['category']
        highest_amount = category_data[0]['total']
    today = timezone.localdate()
    current_month = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    )
    current_income = current_month.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    current_expenses = current_month.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    current_month_key = today.strftime('%Y-%m')
    monthly_budget = Budget.objects.filter(
        user=request.user,
        month=current_month_key
    ).first()
    budget_amount = (
        monthly_budget.amount
        if monthly_budget else Decimal('0.00')
    )
    if budget_amount > 0:
        budget_utilization = (
            current_expenses / budget_amount
        ) * Decimal('100')
    else:
        budget_utilization = None
    first_day = today.replace(day=1)
    previous_month = first_day - timedelta(days=1)
    previous_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=previous_month.year,
        date__month=previous_month.month
    )
    previous_income = previous_transactions.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    previous_expenses = previous_transactions.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    current_category_totals = current_month.filter(
        transaction_type='Expense'
    ).values('category').annotate(total=Sum('amount'))
    previous_category_totals = previous_transactions.filter(
        transaction_type='Expense'
    ).values('category').annotate(total=Sum('amount'))
    previous_category_map = {
        item['category']: item['total']
        for item in previous_category_totals
    }
    unusual_expenses = []
    for item in current_category_totals:
        category = item['category']
        current_amount = item['total']
        previous_amount = previous_category_map.get(
            category,
            Decimal('0.00')
        )
        if previous_amount > 0:
            increase = (
                (current_amount - previous_amount)
                / previous_amount
            ) * Decimal('100')

            if increase >= 50:
                unusual_expenses.append({
                    'category': category,
                    'current_amount': current_amount,
                    'previous_amount': previous_amount,
                    'increase': round(increase, 2),
                })

    if current_income > 0:
        current_savings_rate = (
            (current_income - current_expenses)
            / current_income
        ) * Decimal('100')
    else:
        current_savings_rate = Decimal('0.00')

    if income > 0:
        savings_rate = (
            (income - total_expenses) / income
        ) * Decimal('100')
    else:
        savings_rate = Decimal('0.00')

    risky_patterns = []

    if income > 0 and total_expenses > income:
        risky_patterns.append(
            "Warning! Your expenses exceed your total income. "
            "Review your spending immediately."
        )

    if income > 0 and highest_category:
        if highest_amount > income * Decimal('0.40'):
            risky_patterns.append(
                f"High spending detected in {highest_category}. "
                "This category accounts for more than 40% of your income."
            )

    if income > 0 and savings_rate < Decimal('10'):
        risky_patterns.append(
            "Your savings rate is below 10%. "
            "Try reducing unnecessary expenses."
        )

    if previous_expenses > 0:
        if current_expenses > previous_expenses * Decimal('1.50'):
            risky_patterns.append(
                "Your expenses increased by more than 50% "
                "compared with the previous month."
            )

    if not risky_patterns:
        risky_patterns.append(
            "No major risky spending patterns detected."
        )

    if savings_rate >= 20:
        savings_score = 30
    elif savings_rate >= 10:
        savings_score = 20
    elif savings_rate > 0:
        savings_score = 10
    else:
        savings_score = 0

    if income > 0:

        expense_ratio = (
            total_expenses / income
        ) * Decimal('100')

        if expense_ratio <= 50:
            expense_score = 30
        elif expense_ratio <= 70:
            expense_score = 20
        elif expense_ratio <= 90:
            expense_score = 10
        else:
            expense_score = 0

    else:
        expense_score = 0

    if budget_amount <= 0:
        budget_score = 0
    elif budget_utilization <= 50:
        budget_score = 20
    elif budget_utilization <= 75:
        budget_score = 15
    elif budget_utilization <= 90:
        budget_score = 10
    elif budget_utilization <= 100:
        budget_score = 5
    else:
        budget_score = 0

    if income > 0 and total_expenses < income:
        income_score = 20
    elif income > 0 and total_expenses == income:
        income_score = 10
    else:
        income_score = 0

    financial_health_score = (
        savings_score
        + expense_score
        + budget_score
        + income_score
    )

    if financial_health_score >= 80:
        financial_health_status = "Excellent"
    elif financial_health_score >= 60:
        financial_health_status = "Good"
    elif financial_health_score >= 40:
        financial_health_status = "Average"
    else:
        financial_health_status = "Needs Improvement"

    suggestions = []

    if total_expenses == 0:
        suggestions.append(
            "Add expenses to receive spending analysis."
        )
    else:

        if income > 0 and total_expenses > income * Decimal('0.8'):
            suggestions.append(
                "Your expenses are above 80% of your income. "
                "Try reducing unnecessary spending."
            )

        if highest_category:
            suggestions.append(
                f"Your highest spending category is {highest_category}. "
                f"You spent ₹{highest_amount}."
            )

        if balance > 0:
            suggestions.append(
                f"Your current balance is ₹{balance}. "
                "Consider saving a portion of it."
            )
        else:
            suggestions.append(
                "Your expenses are equal to or greater than your income. "
                "Review your spending."
            )

    if previous_expenses > 0:

        change = (
            (current_expenses - previous_expenses)
            / previous_expenses
        ) * Decimal('100')

        if change > 0:
            suggestions.append(
                f"Your expenses increased by {change:.1f}% "
                "compared with last month."
            )

        elif change < 0:
            suggestions.append(
                f"Your expenses decreased by {abs(change):.1f}% "
                "compared with last month."
            )

    elif current_expenses > 0:
        suggestions.append(
            "You have expenses this month but no previous-month "
            "expenses to compare."
        )

    context = {
        'income': income,
        'total_expenses': total_expenses,
        'balance': balance,
        'highest_category': highest_category,
        'highest_amount': highest_amount,
        'category_data': category_data,
        'suggestions': suggestions,
        'current_income': current_income,
        'current_expenses': current_expenses,
        'previous_income': previous_income,
        'previous_expenses': previous_expenses,
        'savings_rate': round(savings_rate, 2),
        'current_savings_rate': round(current_savings_rate, 2),
        'unusual_expenses': unusual_expenses,
        'risky_patterns': risky_patterns,
        'savings_score': savings_score,
        'expense_score': expense_score,
        'budget_score': budget_score,
        'income_score': income_score,
        'budget_amount': budget_amount,
        'budget_utilization': (
            round(budget_utilization, 2)
            if budget_utilization is not None
            else None
        ),
        'financial_health_score': financial_health_score,
        'financial_health_status': financial_health_status,
    }

    return render(
        request,
        'finance/ai_insights.html',
        context
    )


@login_required
def chatbot_response(request):

    if request.method != 'POST':
        return JsonResponse(
            {'reply': 'Please send a message using the chat box.'},
            status=405
        )

    message = request.POST.get('message', '').strip().lower()

    if not message:
        return JsonResponse(
            {'reply': 'Please type a question first.'},
            status=400
        )

    if len(message) > 500:
        return JsonResponse(
            {'reply': 'Please keep your question under 500 characters.'},
            status=400
        )

    user_transactions = Transaction.objects.filter(
        user=request.user
    )

    income = user_transactions.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    expenses = user_transactions.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    balance = income - expenses

    today = timezone.localdate()

    monthly_expenses = user_transactions.filter(
        transaction_type='Expense',
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    monthly_income = user_transactions.filter(
        transaction_type='Income',
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    category_data = user_transactions.filter(
        transaction_type='Expense'
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    highest_category = None
    highest_amount = Decimal('0.00')

    if category_data.exists():
        highest_category = category_data[0]['category']
        highest_amount = category_data[0]['total']

    if any(word in message for word in ['hello', 'hi', 'hey']):

        reply = (
            "Hello! 👋 Welcome to FinBotics. "
            "I can help you understand your income, expenses, "
            "balance, savings and budget."
        )

    elif 'income' in message:

        reply = f"Your total recorded income is ₹{income}. "

        if monthly_income > 0:
            reply += f"Your income this month is ₹{monthly_income}."

    elif any(word in message for word in ['expense', 'spending', 'spent']):

        if 'month' in message or 'monthly' in message:
            reply = f"Your expenses this month are ₹{monthly_expenses}."
        else:
            reply = f"Your total recorded expenses are ₹{expenses}."

    elif 'balance' in message or 'left' in message:

        reply = f"Your current recorded balance is ₹{balance}."

    elif 'saving' in message:

        if income > 0:
            savings_rate = (balance / income) * Decimal('100')

            reply = (
                f"Your current savings rate is {savings_rate:.2f}%. "
            )

            if savings_rate >= 20:
                reply += "Great work! Keep maintaining your savings habit."
            elif savings_rate > 0:
                reply += "Try to increase your savings gradually."
            else:
                reply += (
                    "Your expenses are equal to or greater than "
                    "your income. Review unnecessary spending."
                )
        else:
            reply = (
                "You have no recorded income yet. "
                "Add income transactions to calculate your savings rate."
            )

    elif 'category' in message or 'highest' in message:

        if highest_category:
            reply = (
                f"Your highest spending category is {highest_category}, "
                f"with total expenses of ₹{highest_amount}."
            )
        else:
            reply = "You do not have any recorded expense categories yet."

    elif 'budget' in message:

        current_month_key = today.strftime('%Y-%m')

        budget = Budget.objects.filter(
            user=request.user,
            month=current_month_key
        ).first()

        if budget:
            remaining = budget.amount - monthly_expenses
            reply = (
                f"Your monthly budget is ₹{budget.amount}. "
                f"You have spent ₹{monthly_expenses}. "
                f"Your remaining budget is ₹{remaining}."
            )
        else:
            reply = (
                "You have not set a budget for this month yet. "
                "Open Budget Planner to create one."
            )

    elif any(word in message for word in ['advice', 'suggest', 'reduce', 'improve', 'help']):

        if income == 0:
            reply = (
                "Start by recording your income and expenses. "
                "Then I can provide more useful financial suggestions."
            )

        elif expenses > income:
            reply = (
                "Your expenses are higher than your income. "
                "Review unnecessary purchases, reduce non-essential "
                "spending and set a realistic monthly budget."
            )

        elif balance / income < Decimal('0.20'):
            reply = (
                "Your savings rate is below 20%. "
                "Try tracking daily spending, reducing unnecessary "
                "shopping and setting a regular savings target."
            )

        else:
            reply = (
                "Your recorded income is higher than your expenses. "
                "Continue tracking your spending, follow your budget "
                "and save regularly."
            )

    else:

        reply = (
            "I'm your FinBotics Finance Assistant. 😊 "
            "Try asking me: "
            "'What is my income?', "
            "'How much did I spend?', "
            "'What is my balance?', "
            "'Which category costs me the most?', "
            "'How much did I spend this month?', "
            "'How can I save more?' or "
            "'What is my budget status?'"
        )

    return JsonResponse({'reply': reply})


@login_required
def set_budget(request):

    current_month = timezone.localdate().strftime('%Y-%m')

    budget, created = Budget.objects.get_or_create(
        user=request.user,
        month=current_month,
        defaults={'amount': Decimal('0.00')}
    )

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)

        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget_dashboard')

    else:
        form = BudgetForm(instance=budget)

    return render(
        request,
        'finance/set_budget.html',
        {'form': form}
    )


@login_required
def budget_dashboard(request):

    current_month = timezone.localdate().strftime('%Y-%m')

    budget = Budget.objects.filter(
        user=request.user,
        month=current_month
    ).first()

    today = timezone.localdate()

    total_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='Expense',
        date__year=today.year,
        date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    budget_amount = (
        budget.amount if budget else Decimal('0.00')
    )

    remaining_budget = budget_amount - total_expenses

    exceeded_amount = max(
        Decimal('0.00'),
        -remaining_budget
    )

    if budget_amount > 0:
        budget_percentage = float(
            (total_expenses / budget_amount) * 100
        )
    else:
        budget_percentage = 0

    progress_width = min(budget_percentage, 100)

    if budget_amount <= 0:
        budget_status = "No budget set"
        budget_alert = None
        alert_type = "none"

    elif budget_percentage >= 100:
        budget_status = "Budget exceeded"
        budget_alert = (
            "You have exceeded your monthly budget! "
            "Review your expenses."
        )
        alert_type = "danger"

    elif budget_percentage >= 90:
        budget_status = "Critical: 90% of budget used"
        budget_alert = (
            "Warning! You have used 90% or more of your "
            "monthly budget. Reduce unnecessary spending."
        )
        alert_type = "danger"

    elif budget_percentage >= 75:
        budget_status = "Warning: 75% of budget used"
        budget_alert = (
            "You have used 75% or more of your budget. "
            "Monitor your remaining expenses."
        )
        alert_type = "warning"

    else:
        budget_status = "You are within your budget"
        budget_alert = (
            "Your spending is within the planned budget. "
            "Keep it up!"
        )
        alert_type = "success"

    category_data = Transaction.objects.filter(
        user=request.user,
        transaction_type='Expense',
        date__year=today.year,
        date__month=today.month
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    context = {
        'budget': budget_amount,
        'total_expenses': total_expenses,
        'remaining_budget': remaining_budget,
        'budget_percentage': round(budget_percentage, 1),
        'progress_width': progress_width,
        'budget_status': budget_status,
        'budget_alert': budget_alert,
        'alert_type': alert_type,
        'category_data': category_data,
        'chart_labels': [
            item['category'] for item in category_data
        ],
        'chart_values': [
            float(item['total']) for item in category_data
        ],
        'exceeded_amount': exceeded_amount,
    }

    return render(
        request,
        'finance/budget_dashboard.html',
        context
    )


@login_required
def scam_detection(request):

    result = None
    message = ""

    if request.method == "POST":
        message = request.POST.get("message", "").strip()

        if message:
            result = detect_scam(message)

            ScamDetectionHistory.objects.create(
                user=request.user,
                message=message,
                risk_score=result["risk_score"],
                risk_level=result["risk_level"],
                warnings=result["warnings"],
                recommendations=result["recommendations"]
            )

    history = ScamDetectionHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    total_checks = ScamDetectionHistory.objects.filter(
        user=request.user
    ).count()

    high_risk_count = ScamDetectionHistory.objects.filter(
        user=request.user,
        risk_level="High Risk"
    ).count()

    medium_risk_count = ScamDetectionHistory.objects.filter(
        user=request.user,
        risk_level="Medium Risk"
    ).count()

    low_risk_count = ScamDetectionHistory.objects.filter(
        user=request.user,
        risk_level="Low Risk"
    ).count()

    context = {
        "result": result,
        "message": message,
        "history": history,
        "total_checks": total_checks,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
    }

    return render(
        request,
        "finance/scam_detection.html",
        context
    )


@login_required
def delete_scam_history(request, history_id):

    if request.method == "POST":
        history = get_object_or_404(
            ScamDetectionHistory,
            id=history_id,
            user=request.user
        )

        history.delete()

    return redirect('scam_detection')


@login_required
def savings_goals(request):

    goals = SavingsGoal.objects.filter(
        user=request.user
    ).order_by('-created_at')

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        target_amount = request.POST.get("target_amount")
        saved_amount = request.POST.get("saved_amount", "0")
        deadline = request.POST.get("deadline") or None

        if title and target_amount:

            try:
                target_amount = Decimal(target_amount)
                saved_amount = Decimal(saved_amount)

                if (
                    target_amount > 0
                    and saved_amount >= 0
                    and saved_amount <= target_amount
                ):

                    SavingsGoal.objects.create(
                        user=request.user,
                        title=title,
                        target_amount=target_amount,
                        saved_amount=saved_amount,
                        deadline=deadline
                    )

                    return redirect('savings_goals')

            except (ValueError, TypeError, InvalidOperation):
                pass

    return render(
        request,
        'finance/savings_goals.html',
        {'goals': goals}
    )


@login_required
def add_savings(request, goal_id):

    goal = get_object_or_404(
        SavingsGoal,
        id=goal_id,
        user=request.user
    )

    if request.method == "POST":

        amount = request.POST.get("amount")

        try:
            amount = Decimal(amount)

            if (
                amount > 0
                and goal.saved_amount + amount <= goal.target_amount
            ):

                goal.saved_amount += amount
                goal.save()

        except (ValueError, TypeError, InvalidOperation):
            pass

    return redirect('savings_goals')


@login_required
def delete_savings_goal(request, goal_id):

    if request.method == "POST":

        goal = get_object_or_404(
            SavingsGoal,
            id=goal_id,
            user=request.user
        )

        goal.delete()

    return redirect('savings_goals')


@login_required
def edit_savings_goal(request, goal_id):

    goal = get_object_or_404(
        SavingsGoal,
        id=goal_id,
        user=request.user
    )

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        target_amount = request.POST.get("target_amount")
        deadline = request.POST.get("deadline") or None

        try:
            target_amount = Decimal(target_amount)

            if (
                title
                and target_amount > 0
                and target_amount >= goal.saved_amount
            ):

                goal.title = title
                goal.target_amount = target_amount
                goal.deadline = deadline
                goal.save()

                return redirect('savings_goals')

        except (ValueError, TypeError, InvalidOperation):
            pass

    return render(
        request,
        'finance/edit_savings_goal.html',
        {'goal': goal}
    )