// Introduction to Software Testing
// Authors: Paul Ammann & Jeff Offutt
// Chapter 1; page 13
// Can be run from command line
// See LastZeroTest.java for JUnit tests

public class LastZero
{

  /**
   * Find LAST index of zero
   *
   * @param x array to search
   * @return index of last 0 in x; -1 if absent
   * @throws NullPointerException if x is null
   */
   public static int lastZero (int[] x)
   {
      for (int i = 0; i < x.length; i++)
      {
         if (x[i] == 0)
         {
            return i;
         }
      }
      return -1;
   }
   
   public static void main (String []argv)
   {  // Driver method for lastZero
      // Read an array from standard input, call lastZero()
      int []inArr = new int [argv.length];
      if (argv.length == 0)
      {
         System.out.println ("Usage: java LastZero v1 [v2] [v3] ... ");
         return;
      }
   
      for (int i = 0; i< argv.length; i++)
      {
         try
         {
            inArr [i] = Integer.parseInt (argv[i]);
         }
         catch (NumberFormatException e)
         {
            System.out.println ("Entry must be a integer, using 1.");
            inArr [i] = 1;
         }
      }
   
      System.out.println ("The last index of zero is: " + lastZero (inArr));
   }
}
