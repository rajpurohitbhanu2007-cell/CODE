#include <iostream>
#include <cstring>
using namespace std;

//GLOBAL VARIABLE DECLARATION
char name[40], team[40];
int age;

void display() {
    cout << "Player Name: " << name << endl;
    cout << "Player Team: " << team << endl;
    cout << "Player Age: " << age << endl;
}

void input() {
    cout << "Enter Player Name: " << endl;
    cin >> name;
    cout << "Enter Player Team: " << endl;
    cin >> team;
    cout << "Enter Player Age: " << endl;
    cin >> age;
}

void change(char newName[40], char newTeam[40], int newAge) {
    strcpy(name, newName);
    strcpy(team, newTeam);
    age = newAge;
}

int main() {
    int choice;

    do {
        cout << "-----------Main Menu-----------" << endl;
        cout << "1. Input Player Data" << endl;
        cout << "2. Display Player Data" << endl;
        cout << "3. Change Player Data" << endl;
        cout << "4. Exit" << endl;
        cout << "Enter Your Choice: " << endl;
        cin >> choice;

        switch (choice) {
            case 1:
                input();
                break;
            case 2:
                display();
                break;
            case 3:
                int newAge;
                char newName[40], newTeam[40];
                cout << "Enter Updated Player Name:" << endl;
                cin >> newName;
                cout << "Enter Updated Player Team:" << endl;
                cin >> newTeam;
                cout << "Enter Updated Player Age:" << endl;
                cin >> newAge;
                change(newName, newTeam, newAge);
                break;
            case 4:
                exit(1); //To exit the complete program
                break;
            default:
                cout << "Wrong Choice!" << endl;
        }
    } while (1);

    return 0;
}
