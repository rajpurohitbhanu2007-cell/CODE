#include<iostream>
#include<string>
using namespace std;

class car{
    private:
    string brand, color;
    int modelYear , price, topSpeed;
    public:
    void getdata(){
        cout<<"Enter brand, color, modelYear, price and topSpeed : ";
        cin>>brand>>color>>modelYear>>price>>topSpeed;
    }
    void display(){
        cout<<"Brand : "<<brand<<endl;
        cout<<"Color : "<<color<<endl;
        cout<<"Model Year : "<<modelYear<<endl;
        cout<<"Price : "<<price<<endl;
        cout<<"Top Speed : "<<topSpeed<<endl;
    }
};

int main(){
    car c;
    c.getdata();
    c.display();
    return 0;
}