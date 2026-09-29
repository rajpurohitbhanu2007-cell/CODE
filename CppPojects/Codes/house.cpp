#include<iostream>
using namespace std;
class house{
    public:
    string name;
    int numberOfRooms;
    void getdata(){
        cout<<"Enter house name and number of rooms : ";
        cin>>name>>numberOfRooms;
    }
    void display(){
        cout<<"House name is : "<<name<<endl;
        cout<<"Number of rooms is : "<<numberOfRooms<<endl;
    }
};