import re


def detect_scam(message):

    message = message.lower()

    risk_score = 0
    warnings = []

    # 1. Urgent or threatening language
    urgency_words = [
        "urgent", "immediately", "account blocked",
        "account suspended", "expire today", "last warning"
    ]

    if any(word in message for word in urgency_words):
        risk_score += 15
        warnings.append("Urgent or threatening language detected.")

    # 2. Sensitive banking information detection
    sensitive_words = [
        "share your otp", "enter otp", "send otp",
        "tell me your otp", "provide otp", "verify otp",
        "otp number", "one time password", "upi pin",
        "atm pin", "debit card pin", "credit card pin",
        "card number", "cvv", "security code",
        "bank password", "banking password",
        "net banking password", "internet banking password",
        "bank details", "account details"
    ]

    if any(word in message for word in sensitive_words):
        risk_score += 30
        warnings.append(
            "Request for sensitive banking information detected."
        )

    # 3. Suspicious payment requests
    payment_words = [
        "send money", "transfer money", "pay now",
        "claim your reward", "receive prize", "collect payment"
    ]

    if any(word in message for word in payment_words):
        risk_score += 20
        warnings.append(
            "Potentially suspicious payment or reward request."
        )

    # 4. Suspicious links and APK detection
    suspicious_domains = [
        "bit.ly", "tinyurl.com", "t.co",
        "cutt.ly", "is.gd", "rb.gy", "shorturl.at"
    ]

    suspicious_link_found = any(
        domain in message for domain in suspicious_domains
    )

    apk_found = bool(
        re.search(r'\.apk(?:[?#\s]|$)', message)
    )

    unknown_app_phrases = [
        "install this app",
        "download this apk",
        "install apk",
        "download this application",
        "install this application"
    ]

    unknown_app_found = any(
        phrase in message for phrase in unknown_app_phrases
    )

    if suspicious_link_found:
        risk_score += 25
        risk_score = max(risk_score, 30)
        warnings.append(
            "Shortened or potentially suspicious link detected."
        )

    if apk_found or unknown_app_found:
        risk_score += 25
        risk_score = max(risk_score, 30)
        warnings.append(
            "Potentially unsafe APK or unknown app installation detected."
        )

    # 4B. Fake website and phishing detection
    phishing_domains = [
        "secure-bank-login",
        "bank-verify-account",
        "kyc-update-now",
        "free-government-scheme",
        "government-subsidy-claim",
        "account-unblock"
    ]

    phishing_found = any(
        domain in message for domain in phishing_domains
    )

    phishing_phrases = [
        "verify your bank account through this link",
        "login to claim your subsidy",
        "update your bank details here",
        "enter your banking details to continue",
        "verify your account immediately"
    ]

    phishing_message_found = any(
        phrase in message for phrase in phishing_phrases
    )

    if phishing_found or phishing_message_found:
        risk_score += 25
        warnings.append(
            "Potential fake website or phishing attempt detected."
        )

    # 4C. Suspicious phone number detection
    phone_numbers = re.findall(
        r'(?<!\d)(?:\+91[\s-]?|0)?[6-9]\d{9}(?!\d)',
        message
    )

    contact_phrases = [
        "call this number",
        "call immediately",
        "contact this number",
        "call our customer care",
        "whatsapp this number",
        "call the number below",
        "contact customer support",
        "call us at",
        "reach us at",
        "contact us at",
        "whatsapp us"
    ]

    if phone_numbers and any(
        phrase in message for phrase in contact_phrases
    ):
        risk_score += 20
        warnings.append(
            "Suspicious contact number included in the message."
        )

    # 4D. Remote access app scam detection
    remote_access_apps = [
        "anydesk",
        "teamviewer",
        "airdroid",
        "rustdesk",
        "quicksupport",
        "chrome remote desktop"
    ]

    remote_access_phrases = [
        "share your access code",
        "share your id",
        "give me remote access",
        "allow remote access",
        "install remote support app",
        "connect to your device",
        "share your screen",
        "give screen access"
    ]

    remote_app_found = any(
        app in message for app in remote_access_apps
    )

    remote_phrase_found = any(
        phrase in message for phrase in remote_access_phrases
    )

    if remote_app_found and remote_phrase_found:
        risk_score += 30
        warnings.append(
            "Potential remote access app scam detected."
        )

    # 5. KYC-related pressure
    if "kyc" in message and any(
        word in message
        for word in ["update", "verify", "block", "suspend"]
    ):
        risk_score += 20
        warnings.append(
            "Potentially suspicious KYC verification request."
        )

    # 6. Fake job offers
    job_words = [
        "work from home", "easy part time job",
        "registration fee", "pay joining fee",
        "earn money daily", "guaranteed income"
    ]

    if any(word in message for word in job_words):
        risk_score += 30
        warnings.append(
            "Potential fake job or work-from-home offer detected."
        )

    # 7. Lottery and prize scams
    prize_words = [
        "you won a lottery", "claim your prize",
        "lucky winner", "won a cash prize",
        "lottery winner", "free gift"
    ]

    if any(word in message for word in prize_words):
        risk_score += 20
        warnings.append(
            "Potential lottery or prize scam detected."
        )

    # 8. UPI and QR-code scams
    upi_words = [
        "scan qr code to receive", "scan qr to receive",
        "upi collect request", "approve collect request",
        "enter upi pin to receive", "receive money by scanning"
    ]

    if any(word in message for word in upi_words):
        risk_score += 30
        warnings.append(
            "Suspicious UPI or QR-code payment request detected."
        )

    # 9. Electricity disconnection threats
    electricity_words = [
        "electricity will be disconnected",
        "power supply will be disconnected",
        "electricity bill pending",
        "pay electricity bill immediately"
    ]

    if any(word in message for word in electricity_words):
        risk_score += 25
        warnings.append(
            "Potential fake electricity payment or disconnection threat."
        )

    # 10. Fake loan offers
    loan_words = [
        "instant loan approved", "guaranteed loan",
        "no documents required", "pay processing fee",
        "loan approval fee"
    ]

    if any(word in message for word in loan_words):
        risk_score += 20
        warnings.append(
            "Potential suspicious loan offer detected."
        )

    # 11. Fake bank customer-care messages
    bank_words = [
        "bank customer care", "call this number to unblock",
        "bank account verification", "debit card blocked",
        "credit card blocked", "contact bank support"
    ]

    if any(word in message for word in bank_words):
        risk_score += 20
        warnings.append(
            "Potential fake bank customer-care message detected."
        )

    # 12. Fake parcel delivery messages
    parcel_words = [
        "parcel is on hold", "package delivery failed",
        "pay delivery fee", "customs clearance fee",
        "update delivery address", "parcel will be returned"
    ]

    if any(word in message for word in parcel_words):
        risk_score += 20
        warnings.append(
            "Potential fake parcel delivery message detected."
        )

    # 13. Fake investment offers
    investment_words = [
        "guaranteed returns", "double your money",
        "daily trading profit", "risk free investment",
        "stock market tips", "investment profit guaranteed"
    ]

    if any(word in message for word in investment_words):
        risk_score += 25
        warnings.append(
            "Potential suspicious investment offer detected."
        )

    # 14. Fake government subsidy messages
    subsidy_words = [
        "government subsidy approved", "free government money",
        "claim your subsidy", "pm scheme payment",
        "government benefit payment", "subsidy amount credited"
    ]

    if any(word in message for word in subsidy_words):
        risk_score += 20
        warnings.append(
            "Potential fake government subsidy message detected."
        )

    # 15. Fake police and digital arrest threats
    police_words = [
        "digital arrest", "police case registered",
        "arrest warrant issued", "money laundering case",
        "you are under investigation", "pay to avoid arrest"
    ]

    if any(word in message for word in police_words):
        risk_score += 30
        warnings.append(
            "Potential police impersonation or digital arrest scam detected."
        )

    # Critical scam indicators
    critical_words = [
        "digital arrest",
        "pay to avoid arrest",
        "enter upi pin to receive",
        "share your otp",
        "arrest warrant issued",
        "money laundering case",
        "tell me your otp",
        "send otp",
        "provide otp",
        "one time password"
    ]

    if any(word in message for word in critical_words):
        risk_score = max(risk_score, 70)

    # Keep score within 100
    risk_score = min(risk_score, 100)

    # Determine risk level
    if risk_score >= 60:
        risk_level = "High Risk"
    elif risk_score >= 30:
        risk_level = "Medium Risk"
    else:
        risk_level = "Low Risk"

    # Default warning
    if not warnings:
        warnings.append(
            "No known scam indicators were detected."
        )

    # Safety recommendations
    recommendations = []

    recommendation_rules = [
        ("sensitive banking information",
         "Never share your OTP, UPI PIN, CVV or banking password."),

        ("kyc",
         "Verify KYC requests through your bank's official website or app."),

        ("job",
         "Do not pay registration or joining fees without verifying the employer."),

        ("lottery",
         "Do not pay money to claim an unexpected prize."),

        ("prize",
         "Do not pay money to claim an unexpected prize."),

        ("upi",
         "Never scan an unknown QR code or enter your UPI PIN to receive money."),

        ("electricity",
         "Verify electricity bills through your official electricity provider."),

        ("loan",
         "Verify the lender and loan terms before paying any processing fee."),

        ("bank customer-care",
         "Contact your bank using the official number on its website or card."),

        ("suspicious contact number",
         "Do not call unknown numbers provided in suspicious messages. Verify customer-care numbers through the official website or app."),

        ("remote access app",
         "Never give unknown people remote access to your device. Do not share access codes or screen-control permissions."),

        ("parcel",
         "Verify delivery updates through the courier's official website."),

        ("investment",
         "Verify investment platforms and never trust guaranteed profit claims."),

        ("subsidy",
         "Verify government benefits through the official government portal."),

        ("police",
         "Do not transfer money under threats of arrest. Verify claims with official authorities."),

        ("shortened or potentially suspicious link",
         "Avoid opening unknown shortened links. Check the destination website independently."),

        ("potentially unsafe apk",
         "Do not install APK files from unknown sources. Use trusted app stores."),

        ("phishing",
         "Do not enter banking details through unknown links. Visit your bank's official website directly.")
    ]

    for keyword, recommendation in recommendation_rules:
        if any(keyword in warning.lower() for warning in warnings):
            recommendations.append(recommendation)

    if not recommendations:
        recommendations.append(
            "Stay alert and verify the sender through an official channel."
        )
    # General score explanation
    score_explanation = []

    if risk_score >= 60:
        score_explanation.append(
            "Multiple or serious suspicious indicators were detected."
        )
    elif risk_score >= 30:
        score_explanation.append(
            "Some suspicious patterns were found in this message."
        )
    else:
        score_explanation.append(
            "Few known suspicious patterns were detected."
        )

    # Detailed explanations
    explanation_rules = {
        "Urgent or threatening language detected.":
            "The sender uses urgency or threats to pressure you into acting quickly without verifying the message.",

        "Request for sensitive banking information detected.":
            "The message may be attempting to collect confidential details such as OTP, UPI PIN, CVV or passwords.",

        "Potentially suspicious payment or reward request.":
            "The sender is asking for money or making a reward-related payment request. Verify the request before paying.",

        "Shortened or potentially suspicious link detected.":
            "Shortened links hide their actual destination and may lead to fake websites designed to steal information.",

        "Potentially unsafe APK or unknown app installation detected.":
            "The message mentions an APK file or unknown app installation. Installing apps from untrusted sources can expose your device and personal information to risk.",

        "Potential fake website or phishing attempt detected.":
            "The message contains suspicious website patterns or asks you to enter sensitive information through a link. Verify the website independently before entering any details.",

        "Suspicious contact number included in the message.":
            "The message contains a phone number and asks you to contact it. Scammers may use fake customer-care numbers to obtain banking details, OTPs or payments. Verify the number independently.",

        "Potential remote access app scam detected.":
            "The message mentions a remote-access application and asks for device access or an access code. Scammers may misuse remote access to view sensitive information or control your device. Only use remote support with trusted people and verified support channels.",

        "Potentially suspicious KYC verification request.":
            "Fraudsters may use KYC update messages to trick users into sharing banking details or clicking fake links.",

        "Potential fake job or work-from-home offer detected.":
            "Fraudulent job offers may demand registration fees or joining payments before providing a job.",

        "Potential lottery or prize scam detected.":
            "Unexpected lottery or prize messages may be used to trick people into paying fees or sharing personal information.",

        "Suspicious UPI or QR-code payment request detected.":
            "A QR code or UPI collect request may be used to trick you into approving a payment instead of receiving money.",

        "Potential fake electricity payment or disconnection threat.":
            "Scammers may threaten electricity disconnection to pressure users into making payments through fake links or numbers.",

        "Potential suspicious loan offer detected.":
            "Fake loan providers may promise easy approval and demand advance processing fees.",

        "Potential fake bank customer-care message detected.":
            "Fraudsters may impersonate bank support staff to collect confidential information or redirect you to fake numbers.",

        "Potential fake parcel delivery message detected.":
            "Fake courier messages may request delivery fees or personal details through suspicious links.",

        "Potential suspicious investment offer detected.":
            "Promises of guaranteed or unusually high returns can be a warning sign of investment fraud.",

        "Potential fake government subsidy message detected.":
            "Fraudsters may impersonate government schemes to collect personal information or advance payments.",

        "Potential police impersonation or digital arrest scam detected.":
            "Scammers may impersonate police or government officials and threaten arrest to force victims to transfer money."
    }

    detailed_explanations = []

    for warning in warnings:
        explanation = explanation_rules.get(warning)

        if explanation:
            detailed_explanations.append(explanation)

    if not detailed_explanations:
        detailed_explanations.append(
            "No matching known scam pattern was found. However, this does not guarantee that the message is safe."
        )

    # Return results
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "warnings": warnings,
        "recommendations": recommendations,
        "score_explanation": score_explanation,
        "detailed_explanations": detailed_explanations
    }