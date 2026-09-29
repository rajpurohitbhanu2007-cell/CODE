#include<iostream>
using namespace std;

class Area{
    public:
    int area(int a){
        return a*a;
    }
    int area(int l, int b){
        return l*b;
    }
    float area(float r){
        return 3.14*r*r;
    }
};
int main(){
    Area a;
    int a1,l,b;
    float r;

    cout<<"Enter the side of square: "<<endl;
    cin>>a1;
    cout<<"Area of the Square is : "<<a.area(a1)<<endl;

    cout<<"Enter both Sides of Rectangle with space"<<endl;
    cin>>l>>b;
    cout<<"Area of Rectangle is :"<< a.area(l,b)<<endl;
    
    cout<<"Enter the radius of circle with decimala: "<<endl;
    cin>>r;
    cout<<"Area of Circle is :"<<a.area(r)<<endl;

    return 0;
}