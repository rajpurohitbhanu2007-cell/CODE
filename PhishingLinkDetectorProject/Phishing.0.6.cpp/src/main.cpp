#include <iostream>
#include <string>
#include <vector>
#include <regex> // Required for the IP address check

using namespace std;

// --- Utility Functions ---

// Checks if the URL uses HTTPS.
bool isSecure(const string& url) {
    return url.rfind("https://", 0) == 0;
}

// Checks if the URL is longer than 50 characters.
bool isLong(const string& url) {
    return url.length() > 50;
}

// Checks if the URL is in the blacklist.
bool isInBlacklist(const string& url) {
    vector<string> blacklist = {"evil-site.com", "another-bad-url.org", "phishing-scam.net"};
    for (const string& blacklisted_url : blacklist) {
        if (url.find(blacklisted_url) != string::npos) {
            return true;
        }
    }
    return false;
}

// Checks if the URL has a suspicious TLD.
bool hasSuspiciousTld(const string& url) {
    vector<string> suspiciousTlds = {".zip", ".mov", ".review", ".xyz", ".tk"};
    for (const string& tld : suspiciousTlds) {
        if (url.length() >= tld.length() && url.substr(url.length() - tld.length()) == tld) {
            return true;
        }
    }
    return false;
}

// Checks if the URL has a suspicious keyword.
bool hasSuspiciousKeyword(const string& url) {
    vector<string> keywords = {"login", "verify", "account", "update", "secure", "signin"};
    for (const string& keyword : keywords) {
        if (url.find(keyword) != string::npos) {
            return true;
        }
    }
    return false;
}

// Checks if the URL contains an '@' symbol.
bool containsAtSymbol(const string& url) {
    return url.find('@') != string::npos;
}

// Checks if the URL is an IP address.
bool isIpAddress(const string& url) {
    const regex ipRegex(R"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)");
    return regex_search(url, ipRegex);
}


// --- Main program execution ---
int main() {

    string url;

    // Display welcome message.
    cout << "Welcome to the Phishing Detector ---" << endl;
    cout << "Enter your URL for check: ";

    // Read the URL from the user.
    getline(cin, url);
    cout << "\n--- Analysis Details ---" << endl;

    // Initialize the risk score.
    int risk_score = 0;

    if (!isSecure(url)) {
        cout << "FAIL: URL is not using secure HTTPS. (+2)" << endl;
        risk_score += 2;
    } else {
        cout << "PASS: URL is using HTTPS." << endl;
    }

    if (isLong(url)) {
        cout << "FAIL: URL is very long (> 50 characters). (+1)" << endl;
        risk_score += 1;
    } else {
        cout << "PASS: URL length is reasonable." << endl;
    }

    if (isInBlacklist(url)) {
        cout << "FAIL: URL was found in the blacklist. (+5)" << endl;
        risk_score += 5;
    } else {
        cout << "PASS: URL not found in the blacklist." << endl;
    }
    
    if (hasSuspiciousTld(url)) {
        cout << "FAIL: URL uses a suspicious TLD (e.g., .zip, .xyz). (+3)" << endl;
        risk_score += 3;
    } else {
        cout << "PASS: URL uses a common TLD." << endl;
    }

    if (hasSuspiciousKeyword(url)) {
        cout << "FAIL: URL contains a suspicious keyword (e.g., login, verify). (+2)" << endl;
        risk_score += 2;
    } else {
        cout << "PASS: URL does not contain suspicious keywords." << endl;
    }

    if (containsAtSymbol(url)) {
        cout << "FAIL: URL contains an \"@\" symbol, which can hide the real domain. (+4)" << endl;
        risk_score += 4;
    } else {
        cout << "PASS: URL does not contain an \"@\" symbol." << endl;
    }

    if (isIpAddress(url)) {
        cout << "FAIL: URL is using an IP address instead of a domain name. (+4)" << endl;
        risk_score += 4;
    } else {
        cout << "PASS: URL uses a domain name." << endl;
    }

    // Display final result and classification.
    cout << "\n=============================================" << endl;
    cout << "Final Risk Score: " << risk_score << endl;

    if (risk_score >= 7) {
        cout << "Result: DANGEROUS - HIGH RISK!" << endl;
    } else if (risk_score >= 3) {
        cout << "Result: SUSPICIOUS - MODERATE RISK." << endl;
    } else {
        cout << "Result: SAFE - LOW RISK." << endl;
    }

    cout << "=============================================" << endl;

    return 0;
}
