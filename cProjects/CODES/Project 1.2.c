//adding header line
#include<stdio.h>
#include<math.h>
//Declaring the function
float UsageBill(int unitsConsumed[]);
float finalbill(float amt);//Tax value
float finalbillPostdue(float amt);//penalty value
void printbill(float amt,int accNo,float amtPostdue);
//==============================================================================

//Main function starts

int main() {
    int accNo;
    int unitsConsumed[3]; //for storing values for past 3 months
    printf("Welcome to the Electric Bill Application\n\n");
    //Start gethering values

    printf("Enter the Account number to proceed : ");
    scanf("%d",&accNo);

    printf("Enter the units consumed in past 3 months : ");
    for(int i = 0; i<3; i++) {
        scanf("%d",&unitsConsumed[i]);
    }
    //End gethering inputs
    //function call to get Usage_bill
    float UsageAmount = UsageBill(unitsConsumed);
        if(UsageAmount<0){
        printf("Invalid input entered");
        printf("terminating the problem.....");
        }
        else{
        float finalAmount = finalbill(UsageAmount);// first function call
        float finalAmountPostdue = finalbillPostdue(finalAmount);//second function call 
        printbill(finalAmount,accNo,finalAmountPostdue);
        }
    
    return 0;
}
//==============================================================================
//Function definations
float UsageBill(int unitsConsumed[]){//function name = Usage_bill
    //declaring variables 
    int totalUnits = 0;
    int fixedCharge;
    float EnergyCharge;
    for(int i = 0;i<3;i++){//data validation check 
        if(unitsConsumed[i]>=0){
        totalUnits = totalUnits + unitsConsumed[i];
        }
        else{
        return -1;//erroneous data is dealt here
        }
    }
    printf("Total units consumed is :%d",totalUnits);
    
    //decide tariff with if else ladder 
    if(totalUnits>=0 && totalUnits<=100){
        fixedCharge = 3;
        EnergyCharge = 0.25;
    }
    else if(totalUnits>=101 && totalUnits<=300){
        fixedCharge = 7;
        EnergyCharge = 0.50;
    }
    else if(totalUnits>=301 && totalUnits<=500){
        fixedCharge = 10;
        EnergyCharge = 0.75;
    }
    else{//anything more than 500
        fixedCharge = 12;
        EnergyCharge = 1.00;
    }
    //let's print all the variable values
    printf("\nCharges leaved as :\n");
    printf("Fixed Charges : $%d",fixedCharge);
    printf("\nEnergy Charges : $%.2f per unit\n",EnergyCharge);
    return fixedCharge + (totalUnits * EnergyCharge);
}

float finalbill(float amt){
    return ceil(amt + ((0.5/100)*amt));
}
float finalbillPostdue(float amt){
    return ceil(amt + ((5/100)*amt));
}
void printbill(float amt,int accNo,float amtPostdue){
  
    for(int i = 0;i<15;i++){
    printf("*");
    }
   
    printf("\nAccount No. : %d",accNo);
    printf("\nFinal Amount: %.0f",amt);
    printf("\nFinal Amount Post Due: %.0f\n",amtPostdue);
   
    for(int i = 0;i < 15;i++){
    printf("*");
    }
}