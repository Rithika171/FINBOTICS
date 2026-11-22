from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]
    CATEGORY_CHOICES = [
        ('Salary', 'Salary'),
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Education', 'Education'),
        ('Bills', 'Bills'),
        ('Healthcare', 'Healthcare'),
        ('Other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    month = models.CharField(max_length=7)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'month'],
                name='unique_user_monthly_budget'
            )
        ]
    def __str__(self):
        return f"{self.user.username} - {self.month}"
class ScamDetectionHistory(models.Model):

       user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

       message = models.TextField()

       risk_score = models.IntegerField()

       risk_level = models.CharField(max_length=20)

       warnings = models.JSONField(default=list)

       recommendations = models.JSONField(default=list)

       created_at = models.DateTimeField(auto_now_add=True)

       def __str__(self):
        return f"{self.risk_level} - {self.risk_score}/100"
class SavingsGoal(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=100)

    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    saved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    deadline = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def progress(self):
        if self.target_amount > 0:
            return min(
                100,
                (self.saved_amount / self.target_amount) * 100
            )
        return 0

    @property
    def remaining_amount(self):
        return max(
            0,
            self.target_amount - self.saved_amount
        )