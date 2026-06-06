package szu.csse.softwaretesting.ch1;


public class FindLast2 {
	  /**
	    * Find last index of element
	    * 
	    *  @param x array to search
	    *  @param y value to look for
	    *  @return last index of y in x; -1 if absent
	    *  @throws NullPointerException if x is null
	    */
	   public static int findLast (int[] x, int y)
	   { 
	      // As the example in the book points out, this loop should end at 0.
		  System.out.print("1,"); //INSTRUMENT, for node i = x.length-1
		  System.out.print("2,"); //INSTRUMENT, for node i > 0
	      for (int i= x.length-1; 
	    		  i > 0; 
	    		  i--)
	      {
	    	 System.out.print("3,"); //INSTRUMENT, for node x[i] == y 
	         if (x[i] == y) 
	         {
	        	System.out.println("4"); //INSTRUMENT, for node return i
	            return i;
	         }
	         System.out.print("5,"); //INSTRUMENT, for node i--
	         System.out.print("2,"); //INSTRUMENT, for node i > 0
	      }
	      System.out.println("6"); //INSTRUMENT, for node return -1 
	      return -1;
	   }

		public static void main(String[] args) {
			// TODO Auto-generated method stub
			int []inArr = {2,3,5};
			int i = 3; //tc4
			int res = findLast(inArr, i);
			//expected: 0
			if (res == 0) {
				System.out.println("Pass");
			}
			else {
				System.out.println("Fail");
			}
			
		}
		


}


