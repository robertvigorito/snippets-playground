
kernel SaturationKernel : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> src; // the input image
  Image<eWrite> dst; // the output image

  param:
    float saturation; // This parameter is made available to the user.

  local:
    float3 coefficients;  // This local variable is not exposed to the user.

  // In define(), parameters can be given labels and default values.
  void define() {
    defineParam(saturation, "Saturation", 1.2f);
  }

  // The init() function is run before any calls to process().
  // Local variables can be initialized here.
  void init() {
    // Initialise coefficients according to rec. 709 standard.
    coefficients.x = 0.2126f;
    coefficients.y = 0.7152f;
    coefficients.z = 0.0722f;
  }

  void process() {
    // Read the input image
    SampleType(src) input = src();

    // Isolate the RGB components
    float3 srcPixel(input.x, input.y, input.z);

    // Calculate luma
    float luma = srcPixel.x * coefficients.x
               + srcPixel.y * coefficients.y
               + srcPixel.z * coefficients.z;
    // Apply saturation
    float3 saturatedPixel = (srcPixel - luma) * saturation + luma;

    // Write the result to the output image
    dst() = float4(saturatedPixel.x, saturatedPixel.y, saturatedPixel.z, input.w);
  }
};
