#include <iostream>
#include <string>
#include <sstream>
#include <random>
#include <cctype>

#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;


// =====================================================
// GLOBAL VARIABLES
// =====================================================

string generatedOTP = "";
string userPhone = "";


// =====================================================
// GENERATE 6 DIGIT OTP
// =====================================================

string generateOTP()
{
    random_device rd;
    mt19937 gen(rd());

    uniform_int_distribution<int> dist(100000, 999999);

    return to_string(dist(gen));
}


// =====================================================
// CHECK MOBILE NUMBER
// =====================================================

bool isValidPhone(string phone)
{
    if (phone.length() != 10)
        return false;

    for (char c : phone)
    {
        if (!isdigit(c))
            return false;
    }

    return true;
}


// =====================================================
// PAGE STYLE
// =====================================================

string pageStyle()
{
    return R"(
<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Arial,sans-serif;
    background:#f4f8fc;
    color:#172033;
}

/* NAVBAR */

nav{
    height:70px;
    background:white;
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 50px;
    border-bottom:1px solid #e4eaf0;
}

.logo{
    font-size:24px;
    font-weight:bold;
    color:#1264d8;
}

nav a{
    text-decoration:none;
    color:#344054;
    margin-left:25px;
    font-weight:bold;
}

/* CONTAINER */

.container{
    max-width:1150px;
    margin:35px auto;
    padding:20px;
}

/* HERO */

.hero{
    background:linear-gradient(135deg,#eaf4ff,#ffffff);
    border-radius:20px;
    padding:60px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.hero h1{
    font-size:48px;
    margin:10px 0;
}

.hero p{
    font-size:18px;
    color:#667085;
}

/* BUTTON */

.btn{
    display:inline-block;
    background:#1264d8;
    color:white;
    border:0;
    border-radius:8px;
    padding:14px 25px;
    text-decoration:none;
    font-weight:bold;
    cursor:pointer;
}

.btn:hover{
    background:#0b52b5;
}

/* CARD */

.card{
    background:white;
    border-radius:16px;
    padding:25px;
    box-shadow:0 5px 20px #00000010;
    margin-bottom:20px;
}

/* INPUT */

input,select{
    width:100%;
    padding:13px;
    margin:8px 0 15px;
    border:1px solid #d5dce6;
    border-radius:8px;
    font-size:16px;
}

input:focus{
    outline:none;
    border-color:#1264d8;
}

/* GRID */

.grid{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:20px;
}

/* SIDEBAR */

.sidebar{
    width:230px;
    position:fixed;
    top:70px;
    bottom:0;
    background:white;
    padding:25px;
    border-right:1px solid #e4eaf0;
}

.sidebar a{
    display:block;
    padding:14px;
    margin-bottom:8px;
    text-decoration:none;
    color:#344054;
    border-radius:8px;
}

.sidebar a:hover{
    background:#eaf4ff;
    color:#1264d8;
}

/* MAIN */

.main{
    margin-left:230px;
    padding:35px;
}

/* MAP */

.map{
    height:350px;
    background:
      linear-gradient(45deg,#dce7d8 25%,transparent 25%),
      linear-gradient(-45deg,#dce7d8 25%,transparent 25%),
      #edf3ea;

    background-size:80px 80px;

    border-radius:15px;

    position:relative;

    overflow:hidden;
}

.road{
    position:absolute;
    background:white;
    height:35px;
    width:120%;
    top:150px;
    left:-20px;
    transform:rotate(-8deg);
}

.ambulance{
    position:absolute;
    background:#e63946;
    color:white;
    padding:10px 15px;
    border-radius:8px;
    font-weight:bold;
    top:125px;
    left:48%;
}

.location{
    position:absolute;
    background:#1264d8;
    color:white;
    padding:8px 12px;
    border-radius:50%;
}

/* SUCCESS */

.success{
    background:#e7f8ed;
    color:#16834b;
    padding:18px;
    border-radius:10px;
    margin-bottom:20px;
}

/* ERROR */

.error{
    background:#ffe8e8;
    color:#d92d20;
    padding:18px;
    border-radius:10px;
    margin-bottom:20px;
}

/* TIMELINE */

.timeline{
    border-left:3px solid #1264d8;
    padding-left:20px;
}

.timeline div{
    margin:25px 0;
}

/* BADGE */

.badge{
    display:inline-block;
    padding:7px 12px;
    background:#eaf4ff;
    color:#1264d8;
    border-radius:20px;
    font-size:13px;
    font-weight:bold;
}

/* EMERGENCY BUTTON */

.emergency{
    height:75px;
    background:white;
    border:1px solid #d5dce6;
    border-radius:8px;
    font-weight:bold;
    cursor:pointer;
}

.emergency:hover{
    border-color:#1264d8;
}

/* OTP */

.otp-box{
    text-align:center;
    max-width:500px;
    margin:80px auto;
}

.otp-input{
    text-align:center;
    font-size:25px;
    letter-spacing:8px;
}

/* RESPONSIVE */

@media(max-width:800px){

    nav{
        padding:0 15px;
        height:auto;
        min-height:70px;
    }

    nav a{
        margin-left:8px;
        font-size:12px;
    }

    .hero,
    .grid{
        display:block;
    }

    .hero{
        padding:30px;
    }

    .hero h1{
        font-size:35px;
    }

    .sidebar{
        position:relative;
        width:100%;
        top:0;
    }

    .main{
        margin-left:0;
        padding:20px;
    }
}

</style>
)";
}


// =====================================================
// HEADER
// =====================================================

string header(string title)
{
    return "<!DOCTYPE html><html><head>"
           "<meta charset='UTF-8'>"
           "<meta name='viewport' content='width=device-width,initial-scale=1'>"
           "<title>" + title + "</title>"
           + pageStyle() +
           "</head><body>";
}


// =====================================================
// FOOTER
// =====================================================

string footer()
{
    return R"(
<footer style="
    background:white;
    text-align:center;
    padding:25px;
    margin-top:40px;
    border-top:1px solid #e4eaf0;
">
    <b>🚑 Ambulance Tracker</b>
    <p>Emergency Ambulance Management System</p>
</footer>
</body>
</html>
)";
}


// =====================================================
// LANDING PAGE / LOGIN
// =====================================================

string landingPage()
{
    return header("Ambulance Tracker") +

R"(
<nav>

    <div class="logo">
        🚑 Ambulance Tracker
    </div>

    <div>
        <a href="/">Home</a>
        <a href="/request">Request Ambulance</a>
        <a href="/driver">Driver</a>
        <a href="/hospital">Hospital</a>
    </div>

</nav>


<div class="container">

    <div class="hero">

        <div>

            <span class="badge">
                24/7 Emergency Service
            </span>

            <h1>
                Fast Ambulance<br>
                When You Need It
            </h1>

            <p>
                Request and track an ambulance quickly
                during an emergency.
            </p>

            <a class="btn" href="#login">
                Request Ambulance
            </a>

        </div>

        <div style="font-size:150px;">
            🚑
        </div>

    </div>


    <!-- LOGIN -->

    <div class="card"
         id="login"
         style="max-width:500px;margin:35px auto;">

        <h2>
            📱 Login with Mobile Number
        </h2>

        <p>
            Enter your 10-digit mobile number
            to receive an OTP.
        </p>


        <form action="/send-otp" method="POST">

            <label>
                Contact Number
            </label>

            <input
                type="tel"
                name="phone"
                maxlength="10"
                placeholder="Enter 10 digit mobile number"
                required
            >


            <button
                class="btn"
                type="submit"
            >
                Send OTP
            </button>

        </form>

    </div>

</div>
)" + footer();
}


// =====================================================
// OTP PAGE
// =====================================================

string otpPage()
{
    return header("Verify OTP") +

R"(
<div class="container">

    <div class="card otp-box">

        <h1>
            🔐 Verify OTP
        </h1>

        <p>
            A 6-digit OTP has been generated
            for your mobile number.
        </p>

        <p>
            Enter the OTP below.
        </p>


        <form action="/verify-otp" method="POST">

            <label>
                Enter OTP
            </label>

            <input
                class="otp-input"
                type="text"
                name="otp"
                maxlength="6"
                placeholder="------"
                required
            >


            <button
                class="btn"
                type="submit"
            >
                Verify OTP
            </button>

        </form>


        <br>

        <a href="/">
            Change Mobile Number
        </a>

    </div>

</div>
)" + footer();
}


// =====================================================
// INVALID OTP PAGE
// =====================================================

string invalidOTPPage()
{
    return header("Invalid OTP") +

R"(
<div class="container">

    <div class="card otp-box">

        <div class="error">

            <h2>
                ❌ Invalid OTP
            </h2>

            <p>
                The OTP you entered is incorrect.
            </p>

        </div>


        <a class="btn" href="/">

            Try Again

        </a>

    </div>

</div>
)" + footer();
}


// =====================================================
// LOGIN SUCCESS PAGE
// =====================================================

string loginSuccessPage()
{
    return header("Login Successful") +

R"(
<div class="container">

    <div class="card otp-box">

        <div class="success">

            <h2>
                ✓ Login Successful
            </h2>

            <p>
                Your mobile number has been verified.
            </p>

        </div>


        <a class="btn" href="/request">

            🚑 Request Ambulance

        </a>

    </div>

</div>
)" + footer();
}


// =====================================================
// REQUEST AMBULANCE PAGE
// =====================================================

string requestPage()
{
    return header("Request Ambulance") +

R"(
<div class="sidebar">

    <h2>
        🚑 Ambulance
    </h2>

    <a href="/">
        Dashboard
    </a>

    <a href="/request">
        Request Ambulance
    </a>

    <a href="/tracking">
        Live Tracking
    </a>

    <a href="/driver">
        Driver Dashboard
    </a>

    <a href="/hospital">
        Hospital Dashboard
    </a>

</div>


<div class="main">

    <h1>
        Request Ambulance
    </h1>

    <p>
        Provide emergency and pickup information.
    </p>


    <div class="grid">


        <!-- PICKUP -->

        <div class="card">

            <h2>
                Pickup Location
            </h2>


            <label>
                Your Location
            </label>

            <input
                type="text"
                name="location"
                placeholder="Enter pickup location"
            >


            <label>
                Emergency Type
            </label>


            <div class="grid">

                <button class="emergency">
                    Medical
                </button>

                <button class="emergency">
                    Accident
                </button>

                <button class="emergency">
                    Critical
                </button>

                <button class="emergency">
                    Other
                </button>

            </div>

        </div>


        <!-- PATIENT -->

        <div class="card">

            <h2>
                Patient Information
            </h2>


            <form
                action="/request"
                method="POST"
            >

                <label>
                    Patient Name
                </label>

                <input
                    type="text"
                    name="patient"
                    placeholder="Patient name"
                    required
                >


                <label>
                    Contact Number
                </label>

                <input
                    type="tel"
                    name="phone"
                    maxlength="10"
                    placeholder="Contact number"
                    required
                >


                <label>
                    Destination Hospital
                </label>

                <input
                    type="text"
                    name="hospital"
                    placeholder="Hospital name"
                    required
                >


                <button
                    class="btn"
                    type="submit"
                >
                    🚑 Request Ambulance
                </button>

            </form>

        </div>

    </div>


    <!-- MAP -->

    <div class="card">

        <h2>
            Pickup Map
        </h2>


        <div class="map">

            <div class="road"></div>

            <div
                class="location"
                style="top:80px;left:30%;"
            >
                A
            </div>

            <div
                class="location"
                style="top:220px;left:70%;"
            >
                H
            </div>

        </div>

    </div>

</div>
)" + footer();
}


// =====================================================
// TRACKING PAGE
// =====================================================

string trackingPage()
{
    return header("Live Tracking") +

R"(
<div class="sidebar">

    <h2>
        🚑 Ambulance
    </h2>

    <a href="/">
        Dashboard
    </a>

    <a href="/request">
        Request Ambulance
    </a>

    <a href="/tracking">
        Live Tracking
    </a>

    <a href="/driver">
        Driver Dashboard
    </a>

    <a href="/hospital">
        Hospital Dashboard
    </a>

</div>


<div class="main">

    <div class="success">

        <h2>
            ✓ Ambulance Request Confirmed
        </h2>

        <p>
            Your ambulance is on the way.
        </p>

    </div>


    <h1>
        Live Tracking
    </h1>


    <div class="card">

        <div class="map">

            <div class="road"></div>

            <div
                class="location"
                style="top:70px;left:15%;"
            >
                P
            </div>


            <div class="ambulance">

                🚑 Ambulance

            </div>


            <div
                class="location"
                style="top:250px;right:15%;"
            >
                H
            </div>

        </div>

    </div>


    <div class="grid">


        <!-- TRIP STATUS -->

        <div class="card">

            <h2>
                Trip Status
            </h2>


            <div class="timeline">

                <div>
                    <b>
                        Request Received
                    </b>
                    <br>
                    Completed
                </div>


                <div>
                    <b>
                        Ambulance Dispatched
                    </b>
                    <br>
                    Completed
                </div>


                <div>
                    <b>
                        Driver En Route
                    </b>
                    <br>
                    Currently travelling
                </div>


                <div>
                    <b>
                        Hospital Arrival
                    </b>
                    <br>
                    Estimated soon
                </div>

            </div>

        </div>


        <!-- DRIVER -->

        <div class="card">

            <h2>
                Driver Details
            </h2>

            <h3>
                Raj Kumar
            </h3>

            <p>
                Ambulance: RJ 14 AB 1234
            </p>

            <p>
                Contact: +91 98765 43210
            </p>


            <hr>


            <h2>
                ETA
            </h2>

            <h1 style="color:#1264d8;">
                8 min
            </h1>

        </div>

    </div>

</div>
)" + footer();
}


// =====================================================
// DRIVER PAGE
// =====================================================

string driverPage()
{
    return header("Driver Dashboard") +

R"(
<div class="sidebar">

    <h2>
        🚑 Driver
    </h2>

    <a href="/">
        Home
    </a>

    <a href="/driver">
        Dashboard
    </a>

    <a href="/tracking">
        Live Tracking
    </a>

</div>


<div class="main">

    <h1>
        Driver Dashboard
    </h1>


    <div class="card">

        <span class="badge">
            NEW REQUEST
        </span>


        <h2>
            Emergency Ambulance Request
        </h2>


        <div class="grid">


            <div>

                <p>
                    <b>Patient</b>
                </p>

                <p>
                    Rahul Sharma
                </p>


                <p>
                    <b>Pickup</b>
                </p>

                <p>
                    Main Market, Dausa
                </p>

            </div>


            <div>

                <p>
                    <b>Hospital</b>
                </p>

                <p>
                    City Hospital
                </p>


                <p>
                    <b>Emergency</b>
                </p>

                <p>
                    Medical Emergency
                </p>

            </div>

        </div>


        <p>
            <b>Contact:</b>
            +91 98765 43210
        </p>


        <form
            action="/driver/accept"
            method="POST"
            style="display:inline;"
        >

            <button
                class="btn"
                type="submit"
            >
                Accept Request
            </button>

        </form>


        <form
            action="/driver/reject"
            method="POST"
            style="display:inline;"
        >

            <button
                class="btn"
                style="background:#dc3545;"
                type="submit"
            >
                Reject
            </button>

        </form>

    </div>


    <div class="card">

        <h2>
            Ongoing Trip
        </h2>

        <p>
            No ongoing trip currently.
        </p>

    </div>

</div>
)" + footer();
}


// =====================================================
// HOSPITAL PAGE
// =====================================================

string hospitalPage()
{
    return header("Hospital Dashboard") +

R"(
<div class="sidebar">

    <h2>
        🏥 Hospital
    </h2>

    <a href="/">
        Home
    </a>

    <a href="/hospital">
        Dashboard
    </a>

    <a href="/tracking">
        Live Tracking
    </a>

</div>


<div class="main">

    <h1>
        Hospital Dashboard
    </h1>


    <div class="success">

        <h2>
            🚑 Incoming Ambulance
        </h2>

        <p>
            Please prepare the emergency department.
        </p>

    </div>


    <div class="grid">


        <!-- AMBULANCE LOCATION -->

        <div class="card">

            <h2>
                Ambulance Location
            </h2>


            <div class="map">

                <div class="road"></div>


                <div class="ambulance">
                    🚑
                </div>


                <div
                    class="location"
                    style="top:250px;right:15%;"
                >
                    🏥
                </div>

            </div>

        </div>


        <!-- PATIENT -->

        <div class="card">

            <h2>
                Patient Information
            </h2>


            <p>
                <b>Patient:</b>
                Rahul Sharma
            </p>


            <p>
                <b>Emergency:</b>
                Medical Emergency
            </p>


            <p>
                <b>Ambulance:</b>
                RJ 14 AB 1234
            </p>


            <p>
                <b>Driver:</b>
                Raj Kumar
            </p>


            <hr>


            <h2>
                Estimated Arrival
            </h2>


            <h1 style="color:#1264d8;">
                8 minutes
            </h1>


            <div class="success">

                Hospital staff should be ready.

            </div>

        </div>

    </div>

</div>
)" + footer();
}


// =====================================================
// HTTP RESPONSE
// =====================================================

string responsePage(string content)
{
    stringstream ss;

    ss << "HTTP/1.1 200 OK\r\n";

    ss << "Content-Type: text/html; charset=UTF-8\r\n";

    ss << "Content-Length: "
       << content.size()
       << "\r\n";

    ss << "Connection: close\r\n";

    ss << "\r\n";

    ss << content;

    return ss.str();
}


// =====================================================
// SEND RESPONSE
// =====================================================

void sendResponse(SOCKET client, string content)
{
    string response = responsePage(content);

    send(
        client,
        response.c_str(),
        (int)response.length(),
        0
    );
}


// =====================================================
// MAIN
// =====================================================

int main()
{
    WSADATA wsaData;


    // START WINDOWS SOCKET

    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0)
    {
        cout << "WSAStartup failed."
             << endl;

        return 1;
    }


    // CREATE SOCKET

    SOCKET serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        IPPROTO_TCP
    );


    if (serverSocket == INVALID_SOCKET)
    {
        cout << "Socket creation failed."
             << endl;

        WSACleanup();

        return 1;
    }


    // SERVER ADDRESS

    sockaddr_in serverAddress{};

    serverAddress.sin_family =
        AF_INET;

    serverAddress.sin_addr.s_addr =
        INADDR_ANY;

    serverAddress.sin_port =
        htons(8080);


    // BIND

    if (bind(
        serverSocket,
        (sockaddr*)&serverAddress,
        sizeof(serverAddress)
    ) == SOCKET_ERROR)
    {
        cout << "Bind failed."
             << endl;

        closesocket(serverSocket);

        WSACleanup();

        return 1;
    }


    // LISTEN

    if (listen(
        serverSocket,
        10
    ) == SOCKET_ERROR)
    {
        cout << "Listen failed."
             << endl;

        closesocket(serverSocket);

        WSACleanup();

        return 1;
    }


    // SERVER MESSAGE

    cout << endl;

    cout << "===================================="
         << endl;

    cout << " Ambulance Tracker Server Started"
         << endl;

    cout << "===================================="
         << endl;

    cout << endl;

    cout << "Open in browser:"
         << endl;

    cout << "http://localhost:8080"
         << endl;

    cout << endl;

    cout << "Press CTRL + C to stop server."
         << endl;

    cout << endl;


    // =================================================
    // SERVER LOOP
    // =================================================

    while (true)
    {
        SOCKET clientSocket =
            accept(
                serverSocket,
                nullptr,
                nullptr
            );


        if (clientSocket ==
            INVALID_SOCKET)
        {
            continue;
        }


        char buffer[8192] = {0};


        int bytesReceived =
            recv(
                clientSocket,
                buffer,
                sizeof(buffer) - 1,
                0
            );


        if (bytesReceived <= 0)
        {
            closesocket(clientSocket);

            continue;
        }


        buffer[bytesReceived] =
            '\0';


        string request(buffer);


        // =================================================
        // HOME PAGE
        // =================================================

        if (request.find("GET / ") == 0)
        {
            sendResponse(
                clientSocket,
                landingPage()
            );
        }


        // =================================================
        // REQUEST PAGE
        // =================================================

        else if (
            request.find("GET /request")
            == 0
        )
        {
            sendResponse(
                clientSocket,
                requestPage()
            );
        }


        // =================================================
        // TRACKING
        // =================================================

        else if (
            request.find("GET /tracking")
            == 0
        )
        {
            sendResponse(
                clientSocket,
                trackingPage()
            );
        }


        // =================================================
        // DRIVER
        // =================================================

        else if (
            request.find("GET /driver")
            == 0
        )
        {
            sendResponse(
                clientSocket,
                driverPage()
            );
        }


        // =================================================
        // HOSPITAL
        // =================================================

        else if (
            request.find("GET /hospital")
            == 0
        )
        {
            sendResponse(
                clientSocket,
                hospitalPage()
            );
        }


        // =================================================
        // SEND OTP
        // =================================================

        else if (
            request.find("POST /send-otp")
            == 0
        )
        {
            /*
                For this simple project,
                we generate a random OTP.

                In a real application,
                connect an SMS API here.
            */

            generatedOTP =
                generateOTP();


            cout << endl;

            cout << "===================================="
                 << endl;

            cout << "          OTP GENERATED"
                 << endl;

            cout << "===================================="
                 << endl;

            cout << "OTP: "
                 << generatedOTP
                 << endl;

            cout << "===================================="
                 << endl;

            cout << endl;


            sendResponse(
                clientSocket,
                otpPage()
            );
        }


        // =================================================
        // VERIFY OTP
        // =================================================

        else if (
            request.find("POST /verify-otp")
            == 0
        )
        {
            /*
                Simple demo verification.

                The browser sends the OTP inside
                the HTTP request.

                We search for the generated OTP
                inside the request.
            */

            if (
                !generatedOTP.empty() &&
                request.find(generatedOTP)
                != string::npos
            )
            {
                cout << endl;

                cout << "OTP Verification: SUCCESS"
                     << endl;

                sendResponse(
                    clientSocket,
                    loginSuccessPage()
                );
            }
            else
            {
                cout << endl;

                cout << "OTP Verification: FAILED"
                     << endl;

                sendResponse(
                    clientSocket,
                    invalidOTPPage()
                );
            }
        }


        // =================================================
        // AMBULANCE REQUEST
        // =================================================

        else if (
            request.find("POST /request")
            == 0
        )
        {
            sendResponse(
                clientSocket,
                trackingPage()
            );
        }


        // =================================================
        // DRIVER ACCEPT
        // =================================================

        else if (
            request.find(
                "POST /driver/accept"
            ) == 0
        )
        {
            sendResponse(
                clientSocket,
                trackingPage()
            );
        }


        // =================================================
        // DRIVER REJECT
        // =================================================

        else if (
            request.find(
                "POST /driver/reject"
            ) == 0
        )
        {
            sendResponse(
                clientSocket,
                driverPage()
            );
        }


        // =================================================
        // UNKNOWN PAGE
        // =================================================

        else
        {
            sendResponse(
                clientSocket,
                landingPage()
            );
        }


        // CLOSE CLIENT

        closesocket(clientSocket);
    }


    // =================================================
    // CLEANUP
    // =================================================

    closesocket(serverSocket);

    WSACleanup();

    return 0;
}