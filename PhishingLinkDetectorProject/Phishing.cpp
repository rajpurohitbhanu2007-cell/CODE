#include <iostream>
#include <string>
#include <fstream>

using namespace std;

// Functions
//function for checking if there is https at the start of the url or not
bool isSecure(const string& url) {
    if (url.rfind("https://", 0) == 0) {
        return true;
    }
    else
        return false;
}
//checking if the url length in to long or not
bool isLong(const string& url) {
    if (url.length() > 50) {
        return true;
    }
    else
        return false;
}
//checking if the url is present in local file of blacklisted urls
bool isInBlacklist(const string& url) {
    ifstream file_in("blacklist.txt");

    if (!file_in.is_open()) {
        cerr << "Warning: Could not open 'blacklist.txt'. Skipping blacklist check." << endl;
        return false;
    }

    string line;
    while (getline(file_in, line)) {
        if (url == line) {
            return true;
        }
    }
    
    file_in.close();
    return false;
}

//the main starts
int main() {
    string url;
    // starting the program 
    cout << "Welcom to the Phishing Detector ---" << endl;
    cout << "Enter your URL for check: ";
    //taking the url as input in url variable 
    cin >> url;
    cout << "\nAnalyzing URL : " << url << endl;
    
    //declaration of variable for storing risk score 
    int risk_score = 0;

    // 1. HTTPS Check
    if (!isSecure(url)) {
        cout << "FAIL (Not using HTTPS)" << endl;
        risk_score += 2;
    } else {
        cout << "PASS (Using HTTPS)" << endl;
    }

    // 2. Length Check
    if (isLong(url)) {
        cout << "FAIL (URL is suspiciously long, > 50 chars)" << endl;
        risk_score += 1;
    } else {
        cout << "PASS (URL length is safe)" << endl;
    }

    // 3. Blacklist Check
    if (isInBlacklist(url)) {
        cout << "FAIL (URL found in blacklist)" << endl;
        risk_score += 5;
    } else {
        cout << "PASS (Not found in blacklist)" << endl;
    }
    
    // 4. Final result 
    cout << "\n=============================================" << endl;
    cout << "Final Risk Score: " << risk_score << endl;

    if (risk_score >= 5) {
        cout << "DANGEROUS - HIGH RISK. Do Not Click!" << endl;
    } else if (risk_score >= 2) {
        cout << "SUSPICIOUS - MODERATE RISK. Proceed with caution." << endl;
    } else {
        cout << "SAFE - LOW RISK. Looks legitimate." << endl;
    }

    cout << "=============================================" << endl;

    return 0;
}
    