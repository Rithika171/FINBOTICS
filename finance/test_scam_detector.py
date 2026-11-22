from finance.scam_detector import detect_scam

test_messages = [
    ("OTP Scam", "Share your OTP immediately to unblock your bank account.", "High Risk"),
    ("UPI QR Scam", "Scan QR code to receive your reward. Enter your UPI PIN.", "High Risk"),
    ("Digital Arrest Scam", "You are under digital arrest. Pay to avoid arrest immediately.", "High Risk"),
    ("Fake Job Scam", "Work from home and pay registration fee to earn money daily.", "Medium Risk"),
    ("Fake Parcel Scam", "Your parcel is on hold. Pay delivery fee immediately.", "Medium Risk"),
    ("Suspicious Phone Number", "Call this number 9876543210 immediately.", "Medium Risk"),
    ("Remote Access Scam", "Install AnyDesk and share your access code immediately.", "Medium Risk"),
    ("Normal Message", "Your order has been delivered successfully. Thank you.", "Low Risk")
]

passed = 0
failed = 0

print("\nFINBOTICS TEST RESULTS")
print("======================")

for name, message, expected in test_messages:

    result = detect_scam(message)
    actual = result["risk_level"]

    print("\nTest Name:", name)
    print("Expected:", expected)
    print("Actual:", actual)
    print("Risk Score:", result["risk_score"])

    if actual == expected:
        print("Status: PASS")
        passed += 1
    else:
        print("Status: FAIL")
        failed += 1

print("\n======================")
print("Total Tests:", len(test_messages))
print("Passed:", passed)
print("Failed:", failed)