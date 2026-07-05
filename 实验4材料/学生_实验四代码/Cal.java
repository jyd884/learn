package szu.csse.softwaretesting.ch8;

public class Cal
{
   public static int cal (int month1, int day1, int month2,
                          int day2, int year)
   {
   //***********************************************************
   // Calculate the number of Days between the two given days in the same year.
   // preconditions : day1 and day2 must be in same year
   //               1 <= month1, month2 <= 12
   //               month1 <= month2
   //               1 <= day1, day2 <= 31
   //               month1 == month2 implies day1 <= day2
   //               The range for year: 1 ... 10000
   //***********************************************************
      validateInputs(month1, day1, month2, day2, year);

      int numDays;

      if (month2 == month1) // in the same month
         numDays  = day2 - day1;
      else
      {
         int daysIn[] = {0, 31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
         // Are we in a leap year?
         int m4 = year % 4;
         int m100 = year % 100;
         int m400 = year % 400;
         if ((m4 != 0) || ((m100 == 0) && (m400 != 0)))
            daysIn[2] = 28;
         else
            daysIn[2] = 29;

         // start with days in the two months
         numDays = day2 + (daysIn[month1] - day1);

         // add the days in the intervening months
         for (int i = month1 + 1; i <= month2-1; i++)
            numDays = daysIn[i] + numDays;
      }
      return (numDays);
   }

   private static void validateInputs(int month1, int day1, int month2, int day2, int year)
   {
      boolean validMonth1 = month1 >= 1 && month1 <= 12;
      boolean validMonth2 = month2 >= 1 && month2 <= 12;
      boolean validOrder = month1 <= month2;
      boolean validDay1 = day1 >= 1 && day1 <= 31;
      boolean validDay2 = day2 >= 1 && day2 <= 31;
      boolean validSameMonthOrder = month1 != month2 || day1 <= day2;
      boolean validYear = year >= 1 && year <= 10000;

      if (!(validMonth1 && validMonth2 && validOrder && validDay1
              && validDay2 && validSameMonthOrder && validYear))
      {
         throw new IllegalArgumentException("Invalid input for cal");
      }
   }

}
