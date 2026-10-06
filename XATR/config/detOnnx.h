#ifndef SRC_DETONNX_H_
#define SRC_DETONNX_H_

#include <string>

#include "MATS.h"


class Detection {
 public:
  Detection() {
    set(0, 0, 8);
  }

  Detection(float *det, size_t len, int ver=8) {
    set(det, len, ver);
  }

  Detection(const Detection &in) {
    dptr_ = in.dptr_;
    len_ = in.len_;
    yolov_ = in.yolov_;
  }

  void set(float *det, size_t len, int ver=8) {
    dptr_ = det;
    len_ = len;
    yolov_ = ver;
  }

  void clear() {
    dptr_ = 0;
    len_ = 0;
  }

  bool empty() {return dptr_ == 0;}

  float x() const {return (dptr_) ? dptr_[0] : 0.0;}
  float y() const {return (dptr_) ? dptr_[1] : 0.0;}
  float width() const {return (dptr_) ? dptr_[2] : 0.0;}
  float height() const {return (dptr_) ? dptr_[3] : 0.0;}

  float score() const {
    // NOTE(Bradley): Yolov5 has a confidence score, but Yolov8 does not.
    if (yolov_ < 8)
      return (dptr_) ? dptr_[4] : 0.0;

    float mx = dptr_[4];
    for (size_t k=5; k < len_; k++)
      mx = (mx < dptr_[k]) ? dptr_[k] : mx;
    return mx;
  }

  float feature(size_t k) const {
    if (k >= len_)
      return 0.0;
    if (yolov_ < 8)
      return (dptr_) ? dptr_[5+k] : 0.0;
    return (dptr_) ? dptr_[4+k] : 0.0;
    }

  float area() const {return (dptr_) ? dptr_[2]*dptr_[3] : 0.0;}

  bool operator<(const Detection &in) const {
    if (!dptr_)
      return (0.0 < in.score());
    return (score() < in.score());
  }

  bool operator>(const Detection &in) const {
    if (!dptr_)
      return (0.0 > in.score());
    return (score() > in.score());
  }

  Detection& operator=(const Detection &in) {
    dptr_ = in.dptr_;
    len_ = in.len_;
    yolov_ = in.yolov_;
    return *this;
  }

 private:
  float *dptr_;
  int yolov_;
  size_t len_;
};


class MATS_LIB detYoloOnnx : public mats::MATS_detector {
 public:
  explicit detYoloOnnx(const char * = 0);
  ~detYoloOnnx();

 private:
  int detect_(const mats::MATS_input_base &input,
      mats::MATS_contact_list &contacts,
      mats::MATS_ecdata_list  &ecdata);

  int configure_(const mats::MATS_struct &cfg);

  int load_engine_(const std::string fn);
  int engine_io_();

  void *engine_;
  void *runtime_;
  void *context_;
  int failure_;
  int yolov_;
  float thresh_;
  float nms_;
  size_t nchan_;
  size_t img_nr_;
  size_t img_nc_;
  size_t ndet_;
  size_t nfeat_;
  std::string model_name_;
  std::string input_node_name_;
  std::vector<std::string> channels_;

};

#endif  // SRC_DETONNX_H_
