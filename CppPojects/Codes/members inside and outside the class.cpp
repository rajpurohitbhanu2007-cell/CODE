#include <iostream>
using namespace std;

class Student {
private:
    int rollNo;
    string name;
public:
    void get_data() {
        cout << "enter no ";
        cin >> rollNo;
    }
    void display_data() {
        cout << "Roll No " << rollNo << endl;
        cout << "Name " << name << endl;
    }
};

int main() {
    Student s1;
    s1.get_data();
    s1.display_data();
    return 0;
}
