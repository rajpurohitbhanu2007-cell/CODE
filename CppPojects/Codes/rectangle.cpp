#include<iostream>
using namespace std;

class Rectangle{
    public:
    int length , breadth;
    void getdata(){
        cout<<"Enter length and breadth : ";
        cin>>length>>breadth;
    }
    void area(){
        cout<<"Area is : "<<length*breadth<<endl;
    }
    void perimeter(){
        cout<<"Perimeter is : "<<2*(length+breadth)<<endl;
    }
};

int main(){
    class Rectangle r;
    r.getdata();
    r.area();
    r.perimeter();
    return 0;
}