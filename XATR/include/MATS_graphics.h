/**
 * @file
 * @brief File contains the MATS_graphic class for creating graphics, the
 * MATS_graphics_display and MATS_graphics_exporter (MGX) module base classes,
 * and the MATS_graphics_manager class.
 */

/**************************************************************************
 *
 * DISTRIBUTION STATEMENT D. Distribution authorized to the Department of
 * Defense and U.S. DoD contractors only; Administrative or Operational Use; 1
 * Jan 2017. Other U.S. requests shall be referred to Naval Surface Warfare
 * Center Panama City Division, ATTN: Technical Director NSWC PCD, 110 Vernon
 * Ave, Panama City, FL 32407.
 *
 * POC:
 *
 * Bradley Marchand
 * NSWC Panama City Division, Code X24 (850)-230-7385
 * bradley.marchand@navy.mil
 *
 * Derek Kolacinski
 * NSWC Panama City Division, Code X23 (850)-230-7218
 * derek.kolacinski@navy.mil
 *
 *************************************************************************/
#ifndef SRC_MATS_GRAPHICS_H_
#define SRC_MATS_GRAPHICS_H_

#include <string>
#include <vector>

#include "MATS_input.h"
#include "MATS_manager.h"


namespace mats {


/**
 * A container for %MATS objects to be rendered to an image for display or
 * writing to a file. This is intended to be a common structure that GRAPHICS
 * modules can use to pass information.
 */
class MATS_LIB MATS_graphic {
 public:
  /**
   * MATS_graphic constructor.
   */
  MATS_graphic();

  /**
   * Constructor that creates MATS_graphic as a child of another MATS_graphic.
   *
   * @param[in] parent Pointer to parent MATS_graphic.
   * @param[in] type Type being constructed, e.g., "image" or "line".
   */
  MATS_graphic(MATS_graphic* parent, const char* type);

  /**
   * Adds an image to the MATS_graphic axis.
   *
   * @param[in] nr Number of rows in image (y-dimension).
   * @param[in] nc Number of columns in image (x-dimension).
   * @param[in] x Values of x-axis (array of @p nc values).  Use null pointer
   * to default to index numbers.
   * @param[in] y Values of y-axis (array of @p nr values).  Use null pointer
   * to default to index numbers.
   * @param[in] img Values of z-axis (array of @p nr x @p nc values).  Array is
   * assumed to be column-major.
   *
   * @return Returns a pointer to the newly created image on success. On
   * failure, returns a null pointer.
   *
   * @note Even though the input image is column-major, the MATS_graphic stores
   * the image as row-major.
   */
  MATS_graphic*
  addImage(size_t nr, size_t nc, const double* x, const double* y,
      const double* img);

  /**
   * Adds a line to the MATS_graphic axis.
   *
   * @param[in] len Number of points in the line.
   * @param[in] x Values of x-axis (array of @p len values).
   * @param[in] y Values of y-axis (array of @p len values).
   *
   * @return Returns a pointer to the newly created line on success. On
   * failure, returns a null pointer.
   */
  MATS_graphic*
  addLine(size_t len, const double* x, const double* y);

  /**
   * Adds an image from a MATS_input or MATS_input_chunk.  If no band is
   * specified, the reference dataset is imaged.
   *
   * @param[in] input Input or chunk containing data to be imaged.
   * @param[in] band (Optional) Name of the band to be imaged.  Defaults to
   * reference band.
   *
   * @return Returns 0 on success.
   */
  int
  addInput(const MATS_input_base& input, const char* band = NULL);

  /**
   * Adds contacts to figure.  A snippet-sized box is drawn around each
   * contact.
   *
   * @param[in] contacts Contact list.
   * @param[in] ecdata Ecdata list.
   *
   * @return Returns 0 on success.
   */
  int
  addContacts(const MATS_contact_list& contacts,
      const MATS_ecdata_list& ecdata);

  /**
   * Gets the size of the graphic.
   *
   * @param[out] nr Number of rows (y-dimension).
   * @param[out] nc Number of columns (x-dimension).
   *
   * @return Returns 0 on success.
   */
  int
  size(size_t& nr, size_t& nc) const;

  /**
   * Renders the MATS_graphic to an output array.
   *
   * @param[in] nchan Number of color channels.
   * @param[in] nr Number of rows in output image (y-dimension).
   * @param[in] nc Number of columns in output image (x-dimension).
   * @param[out] img Output image (row-major array of size @p nr x @p nc x
   * @p nchan).
   *
   * @return Returns 0 on success.
   */
  int
  render(size_t nchan, size_t nr, size_t nc, unsigned char* img) const;

  /**
   * MATS_graphic destructor. Also destroys all children.
   */
  ~MATS_graphic();

 private:
  std::string type_;
  std::vector<size_t> xdims_;
  std::vector<double> x_;
  std::vector<size_t> ydims_;
  std::vector<double> y_;
  std::vector<size_t> zdims_;
  std::vector<double> z_;

  double width_;
  std::string linestyle_;

  void* parent_;
  std::vector<void*> children_;

  int setMainAxis_(size_t nr, size_t nc, const double* x, const double* y);
};


/**
 * Abstract base class for a MATS_graphics_display module.  Each
 * MATS_graphics_display object controls a single figure window.
 */
class MATS_LIB MATS_graphics_display : public MATS_module_base {
 public:
  MATS_graphics_display();

  virtual ~MATS_graphics_display() {};

  /**
   * Opens a figure window.
   *
   * @return Returns 0 on success.
   */
  virtual int figure() = 0;

  /**
   * Plots a scaled image of data.
   *
   * @param[in] input Input or chunk containing data to be imaged.
   *
   * @return Returns 0 on success.
   */
  virtual int imagesc(const MATS_input_base& input) = 0;

  /**
   * Displays contact data on an image plot.
   *
   * @param[in] contacts List of contacts to display.
   * @param[in] ecdata List of ecdata corresponding to @p contacts.
   *
   * @return Returns 0 on success.
   */
  virtual int
  addContacts(const MATS_contact_list& contacts,
      const MATS_ecdata_list& ecdata) = 0;

  /**
   * Saves the figure as a jpeg file.
   *
   * @param[in] filename Filename.
   *
   * @return Returns 0 on success.
   */
  virtual int save(const char* filename) = 0;

  /**
   * Clears the figure window.
   *
   * @return Returns 0 on success.
   */
  virtual int clear() = 0;

  /**
   * Closes the figure window.
   *
   * @return Returns 0 on success.
   */
  virtual int close() = 0;
};


/**
 * Type definition for export function used by a MATS_graphics_exporter (MGX)
 * module.
 */
typedef int (*func_export)(const char*, const MATS_graphic&);


/**
 * Default export function.  Does nothing.
 *
 * @param[in] filename Name of image file to save.
 * @param[in] fig A MATS_graphic containing the image.
 *
 * @return Returns 1.
 */
int
default_export(const char* filename, const MATS_graphic& fig);


/**
 * MATS_graphics_exporter (MGX) modules are used to export images to files.
 * Each MGX module exports to a particular format.
 */
class MATS_LIB MATS_graphics_exporter {
 public:
  MATS_graphics_exporter();

  virtual ~MATS_graphics_exporter() {};

  /**
   * Returns name of export format (file extension) used by this module. Name
   * should be unique from other exporters.
   */
  const char* format() const;

  /**
   * Saves an image with the specified filename.
   *
   * @param[in] filename Name of image file to save.
   * @param[in] fig A MATS_graphic containing the image.
   *
   * @return Returns 0 on success.
   */
  int save(const char* filename, const MATS_graphic& fig) const;

 protected:
  /**
   * Set the image file type (file extension) exported by this module. For
   * example, "tiff" or "jpg".
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] format File extension exported by this module.
   */
  void setFormat(const char* format);

  /**
   * Set the export function for this module.
   *
   * Use this method in the constructor of the derived class.
   *
   * @param[in] ex Export function used by this module.
   */
  void setExport(func_export ex);

 private:
  std::string format_;  /**< File extension supported by this module */
  func_export export_;  /**< Image export function */
};


/**
 * MATS_graphics_manager serves as a collector of MGX modules.
 */
class MATS_LIB MATS_graphics_manager {
 public:
  MATS_graphics_manager();

  /**
   * Returns a list of the supported file formats of known MGX modules.
   */
  std::vector<std::string>
  formats() const;

  /**
   * Returns a pointer to an MGX module corresponding to the given file format.
   *
   * @param[in] format Desired file format (should be all lower-case).
   *
   * @return Returns the pointer to the corresponding MGX module. If none,
   * returns a null pointer.
   */
  const MATS_graphics_exporter*
  MGX(const char* format) const;

  /**
   * Adds new MGX module.
   *
   * @param[in] mgx New MGX module.
   *
   * @return Returns 0 on success. Returns 1 if the MGX module already exists.
   */
  int
  addMGX(const mats::MATS_graphics_exporter& mgx);

 private:
  std::vector<mats::MATS_graphics_exporter> mgxs_;
};


/**
 * Returns a list of supported image file formats for MGX (graphics
 * exporter) modules.
 *
 * @return Returns a vector of supported image file formats.
 * @warning To find supported formats, a MATS_C or MATS object must be created
 * first, which will scan for MGX modules.
 */
MATS_LIB std::vector<std::string>
mats_known_MGXformats();


/**
 * Returns a pointer to requested MGX (graphics exporter) module.
 *
 * @param[in] format Image file format.
 *
 * @return Returns the pointer to the corresponding MGX module. If none,
 * returns a null pointer.
 *
 * @warning To find supported formats, a MATS_C or MATS object must be created
 * first, which will scan for MGX modules.
 */
MATS_LIB const mats::MATS_graphics_exporter*
mats_MGX(const char* format);


/**
 * Adds new MGX module to known MGX modules.
 *
 * @param[in] mgx New MGX module.
 *
 * @return Returns 0 on success. Returns 1 if the MGX module already exists.
 */
MATS_LIB int
mats_MGX_add(const mats::MATS_graphics_exporter& mgx);


/**
 * Assigns a color in the form of Red-Green-Blue (RGB) levels to a value.
 * Last five values (251-255) are assigned red, green, blue, black, white.
 *
 * @param[in] val Input value.
 * @param[out] r Red value.
 * @param[out] g Green value.
 * @param[out] b Blue value.
 */
void
mats_colormap(unsigned char val, unsigned char& r, unsigned char& g,
    unsigned char& b);


/**
 * Converts an image from double precision values to unsigned char values.
 *
 * @param[in] N Number of elements in image.
 * @param[in] data Input image.
 * @param[out] img Output image.
 *
 * @return Returns 0 on success.
 *
 * @warning Output @p img must be pre-allocated to @p N elements.
 */
int
mats_convert_image(size_t N, const double* data, unsigned char* img);

}  // namespace mats

#endif  // SRC_MATS_GRAPHICS_H_
