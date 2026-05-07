
// ** Tel source: test **
//   
//   def even_fib_sub(max):
//       sum = 0
//       first, second = 1, 1
//       while second < max:
//           new = first + second
//           if new % 2 == 0:
//               sum += new
//           first = second
//           second = new
//       return sum

@javax.annotation.processing.Generated("xolir")  // do not edit
public class Euler2 {

	private record Point(
		double x,
		double y
	) {}

	private static void main() {
		evenFibSub(4000000);
		return 0;
	}

	// even_fib_sub
	private static long evenFibSub(
		long max
	) {
		long sum;
		long first;
		long second;
		long new_;
		sum = 0;
		first = 1;
		second = 1;
		while ((second < max)) {
			new_ = (first + second);
			if (((new_ % 2) == 0)) {
				sum = (sum + new_);
			};
			first = second;
			second = new_;
		};
		return sum;
	}

}
