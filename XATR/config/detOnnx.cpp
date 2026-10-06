#include "detOnnx.h"

#include <string>
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>

#include <cuda_runtime_api.h>
#include <NvInfer.h>
#include <NvOnnxParser.h>

#include "MATS_interp.h"
#include "MATS_basic.h"
#include "MATS_data.h"

// Debugging
#include "MATS_hdf5.h"
// #define DETONNX_DEBUG "/home/marchand/Git/PyMATS/"

static int
trt_report_version() {
  std::stringstream msg;
  int vHeader, vLib;

  vHeader = NV_TENSORRT_VERSION;
  vLib = getInferLibVersion();
  msg << "TensorRT Version: " << vHeader << " (header), "
      << vLib << " (library)";
  mats_log(MATS_MSG, msg.str().c_str());

  if (vHeader != vLib) {
    mats_log(MATS_ERROR, "TensorRT header and library versions do not match!");
    return 1;
  }
  return 0;
}


class Logger : public nvinfer1::ILogger {
  void log(Severity severity, const char *msg) noexcept override {
    // std::cerr << "TENSORRT | " << msg << std::endl;
    switch (static_cast<int>(severity)) {
      case 0:
        mats_log(MATS_ERROR, msg);
        break;
      case 1:
        mats_log(MATS_ERROR, msg);
        break;
      case 2:
        mats_log(MATS_WARN, msg);
        break;
      case 3:
        mats_log(MATS_MSG, msg);
        break;
    }
  }
} gLogger;


static std::string
modelname_onnx2eng(const char *model_fn) {
  std::string fn = model_fn;
  if (fn.substr(fn.size()-5).compare(".onnx") == 0) {
    fn = fn.substr(0, fn.size()-5);
  }
  fn += ".eng";
  return fn;
}


static int
get_engine_header(std::string* header) {
  // Generate the expected header for a compatible engine file for this device.
  // The header includes information about:
  //   - Platform (128 char)
  //   - GPU Model (256 char)
  //   - TensorRT version (major, minor, and patch) (128 char)

  std::string platform_str, gpu_str, trt_str;
  size_t platform_len, gpu_len, trt_len;
  std::stringstream msg, trt;
  int devnum;
  cudaDeviceProp devprop;
  cudaError_t status;

  // Length of each section
  platform_len = 128;
  gpu_len = 256;
  trt_len = 128;

  // Platform
#ifdef MATS_WINDOWS
  platform_str = "Windows";
#elif defined(MATS_LINUX)
  platform_str = "Linux";
#else
  mats_log(MATS_ERROR, "Unknown platform; could not generate engine header.");
  return 1;
#endif

  if (sizeof(void*) == 8) {
    platform_str += " 64-bit";
  } else if (sizeof(void*) == 4) {
    platform_str += " 32-bit";
  } else {
    mats_log(MATS_ERROR, "Unknown bitness; could not generate engine header.");
    return 1;
  }

  // GPU Model
  status = cudaGetDevice(&devnum);
  if (status) {
    msg << "cudaGetDevice() returned CUDA error type " << status;
    mats_log(MATS_ERROR, msg.str().c_str());
    return 1;
  }
  status = cudaGetDeviceProperties(&devprop, devnum);
  if (status) {
    msg << "cudaGetDeviceProperties() returned CUDA error type " << status;
    mats_log(MATS_ERROR, msg.str().c_str());
    return 1;
  }
  gpu_str = devprop.name;

  // TensorRT version (major, minor, and patch)
  trt << getInferLibVersion();
  trt_str = trt.str();
  if (trt_str.size() == 0) {
    mats_log(MATS_ERROR,
        "Unknown TensorRT version; could not generate engine header.");
    return 1;
  }

  // Combine strings to make header.
  header->clear();
  platform_str.resize(platform_len);
  gpu_str.resize(gpu_len);
  trt_str.resize(trt_len);
  header->append(platform_str);
  header->append(gpu_str);
  header->append(trt_str);

  return 0;
}


static int
create_engine(const char *onnxFile) {
  nvinfer1::IBuilder *builder = 0;
  nvinfer1::IBuilderConfig *config = 0;
  nvinfer1::INetworkDefinition *network = 0;
  nvonnxparser::IParser *parser = 0;
  nvinfer1::IHostMemory *ser_mem = 0;
  std::string header;
  int status = 0;
  const uint32_t explicit_batch = 1U << static_cast<uint32_t>(
      nvinfer1::NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);

  // std::cerr << "Create Builder\n";
  builder = nvinfer1::createInferBuilder(gLogger);
  if (!builder) {
    mats_log(MATS_ERROR, "Failed to creat builder");
    status = 1;
    goto finish;
  }

  // std::cerr << "Create Builder Configuration\n";
  config = builder->createBuilderConfig();
  if (!config) {
    mats_log(MATS_ERROR, "Failed to create builder config.");
    status = 1;
    goto finish;
  }

  // std::cerr << "Create network\n";
  network = builder->createNetworkV2(explicit_batch);
  if (!network) {
    mats_log(MATS_ERROR, "Failed to create network");
    status = 1;
    goto finish;
  }

  // std::cerr << "Create parser\n";
  parser = nvonnxparser::createParser(*network, gLogger);
  if (!parser->parseFromFile(onnxFile,
      static_cast<int>(nvinfer1::ILogger::Severity::kINFO))) {
    mats_log(MATS_ERROR, "ERROR: could not parse input engine.");
    status = 1;
    goto finish;
  }

  // std::cerr << "Optimize and serialize serialize engine\n";
  ser_mem = builder->buildSerializedNetwork(*network, *config);
  if (ser_mem) {
    std::string eng_fn = modelname_onnx2eng(onnxFile);

    // Back up any existing engine file.
    remove((eng_fn+".bak").c_str());
    rename(eng_fn.c_str(), (eng_fn+".bak").c_str());

    std::ofstream ofs(eng_fn, std::ios::binary | std::ofstream::out);
    // ofs.write(header.c_str(), header.size());
    ofs.write(static_cast<char*>(ser_mem->data()), ser_mem->size());
    ofs.close();
    delete ser_mem;
  } else {
    mats_log(MATS_WARN, "Failed serialization of TensorRT engine.");
  }

  // std::cerr << "Clean up\n";
  finish:
  if (network) delete network;
  if (builder) delete builder;
  if (config) delete config;
  if (parser) delete parser;

  // std::cerr << "All done\n";
  return status;
}


/**
 * Intersection of Union
 */
float
iou(Detection &det1, Detection &det2) {
  float hw1 = det1.width() / 2;
  float hh1 = det1.height() / 2;
  float hw2 = det2.width() / 2;
  float hh2 = det2.height() / 2;

  // Lower left and upper right of box 1 and box 2.
  float x1 = det1.x() - hw1;
  float a1 = det1.x() + hw1;
  float x2 = det2.x() - hw2;
  float a2 = det2.x() + hw2;
  float y1 = det1.y() - hh1;
  float b1 = det1.y() + hh1;
  float y2 = det2.y() - hh2;
  float b2 = det2.y() + hh2;

  // Intersection bounding box size
  float iw = mats::max(0.0f, mats::min(a1, a2) - mats::max(x1, x2));
  float ih = mats::max(0.0f, mats::min(b1, b2) - mats::max(y1, y2));
  float ia = iw * ih;

  // Union area of both the boxes
  float ua = det1.area() + det2.area() - ia;

  return ia / ua;
}



/**
 * Apply non-maximum suppression to avoid detecting too many overlapping
 * bounding boxes for a given object.
 */
void
nms(std::vector<Detection> &dets, float thresh_iou) {
  std::vector<Detection> keep;

  // sort the prediction boxes in P according to their confidence scores
  std::sort(dets.begin(), dets.end());

  while (dets.size() > 0) {
    // Save largest prediction
    keep.push_back(dets.back());
    dets.pop_back();

    // Filter detections with IoU greater than threshold
    for (size_t k=0; k < dets.size(); k++) {
      if (dets[k].empty())
        continue;
      float overlap = iou(keep.back(), dets[k]);
      // std::cerr << "[" << k << "] " << overlap << std::endl;
      if (overlap >= thresh_iou) {
        dets[k].clear();
        continue;
      }
    }

    // Clear out empties
    while (dets.size() > 0 && dets.back().empty())
      dets.pop_back();
  }

  // Push saved predictions back for return
  for (size_t k=0; k < keep.size(); k++)
    dets.push_back(keep[k]);
  return;
}


/*******************************************************************************
 * detYoloOnnx
 ******************************************************************************/

detYoloOnnx::detYoloOnnx(const char*) {
  engine_ = 0;
  runtime_ = 0;
  context_ = 0;
  nms_ = 0.0;

  mats::MATS_cfg matscfg;
  int devnum;  // ordinal for device

  failure_ = trt_report_version();
  if (failure_) {
    return;
  }

  // Get CUDA device ID from default.cfg file.
  if (matscfg.getConfigOption("cudaDeviceId", &devnum)) {
    mats_log(MATS_WARN, "cudaDeviceId option not found. Using default of 0.");
    devnum = 0;
  }

  // CUDA Driver API not available; use CUDA Runtime API only
  cudaError_t status;  // enum type

  // Set CUDA device
  status = cudaSetDevice(devnum);
  if (status) {
    std::stringstream msg;
    msg << "Failed to set CUDA device " << devnum << " (cudaError = "
        << status << ").";
    mats_log(MATS_ERROR, msg.str().c_str());
    return;
  }

  return;
}


detYoloOnnx::~detYoloOnnx() {
  nvinfer1::ICudaEngine *engine = 0;
  nvinfer1::IRuntime *runtime = 0;

  engine = static_cast<nvinfer1::ICudaEngine*>(engine_);
  delete engine;
  runtime = static_cast<nvinfer1::IRuntime*>(runtime_);
  delete runtime;

  engine = 0;
  runtime = 0;
}


int
detYoloOnnx::configure_(const mats::MATS_struct &cfg) {
  std::string model_fn = mats::mats_config_dir();
  nvinfer1::ICudaEngine *engine = 0;
  std::string eng_model;

  // std::cerr << "[detYoloOnnx::configure]\n";
  if (failure_) {
    mats_log(MATS_ERROR, "TensorRT version mismatch.");
    return 1;
  }

  // Create runtime if it does not exist
  if (!runtime_) {
    runtime_ = (void*) nvinfer1::createInferRuntime(gLogger);
    if (!runtime_) {
      mats_log(MATS_ERROR, "Failure creating TensorRT runtime.");
      return 1;
    }
  }

  // Release any existing engine
  if (engine_) {
    engine = static_cast<nvinfer1::ICudaEngine*>(engine_);
    delete engine;
    engine_ = 0;
    engine = 0;
  }

  if (cfg.type("nms") != mats::tDOUBLE)
    nms_ = 0.40;
  else
    nms_ = cfg.get<double>("nms")[0];

  if (cfg.type("thresh") != mats::tDOUBLE)
    thresh_ = 0.1;
  else
    thresh_ = cfg.get<double>("thresh")[0];

  if (cfg.type("yolov") != mats::tINT)
    yolov_ = 8;
  else
    yolov_ = cfg.get<int>("yolov")[0];

  if (cfg.type("modelfile") != mats::tCHAR) {
    mats_log(MATS_ERROR, "Missing or invalid 'modelfile' config value.");
    return 1;
  }
  model_name_ = cfg.get<char>("modelfile");
  mats::file_path(model_fn, model_name_);

  if (!mats::file_exist(model_fn.c_str())) {
    std::stringstream msg;
    msg << "Model file '" << model_fn << "' does not exist.";
    mats_log(MATS_ERROR, msg.str().c_str());
    return 1;
  }

  eng_model = modelname_onnx2eng(model_fn.c_str());
  // std::cerr << eng_model << std::endl;
  if (!mats::file_exist(eng_model.c_str())) {
    if (create_engine(model_fn.c_str())) {
      mats_log(MATS_ERROR, "Failure serializing ONNX file.");
      return 1;
    }
  }

  // std::cerr << "load engine\n";
  if (load_engine_(eng_model.c_str())) {
    // std::cerr << "Failed load of serialized engine file.\n";
    mats_log(MATS_WARN, "Failed load of serialized engine file.");
    return 1;
  }

  // Read network IO sizes
  // std::cerr << "engine io\n";
  engine_io_();

  // std::cerr << "channel allocation\n";
  channels_.resize(3);
  channels_[2] = "IMG-R";
  channels_[1] = "IMG-G";
  channels_[0] = "IMG-B";

  // std::cerr << "[/detYoloOnnx::configure]\n";
  return 0;
}


int
detYoloOnnx::detect_(const mats::MATS_input_base &input,
    mats::MATS_contact_list &contacts, mats::MATS_ecdata_list  &ecdata) {
  cudaStream_t stream;
  void* bindings[2]{0};
  // void *trt_input = 0, *trt_output = 0;
  size_t num_in = nchan_*img_nr_*img_nc_;
  size_t num_out = ndet_*nfeat_;
  size_t nclass = (yolov_ < 8) ? nfeat_ - 5 : nfeat_ - 4;
  size_t nr, nc;
  std::vector<float> img_buff(num_in);
  std::vector<float> results(num_out, 0);
  std::vector<Detection> dets;
  float *rptr = 0;
  float xfactor, yfactor;

  #ifdef DETONNX_DEBUG
  mats_hid_t fid;
  std::vector<size_t> dims(2), dims3(3);
  std::stringstream filename;
  filename << DETONNX_DEBUG << "debug_onnx_detect.h5";
  std::cerr << "DEBUG FILE: " << filename.str() << std::endl;
  fid = mats::mats_H5Fcreate(filename.str().c_str(), 1);
  if (fid <= 0) {return 1;}
  mats::h5_create_mats_input(fid, "input", static_cast<mats::MATS_input>(input));
  #endif

  // std::cerr << "[detYoloOnnx::detect]\n";
  cudaStreamCreate(&stream);
  nvinfer1::ICudaEngine *engine = static_cast<nvinfer1::ICudaEngine*>(engine_);
  nvinfer1::IExecutionContext *context = engine->createExecutionContext();

  if (cudaMalloc(&bindings[0], num_in*sizeof(float)) || !bindings[0]) {
    mats_log(MATS_ERROR, "Failed cudaMalloc allocation for input.");
    goto finish;
  }
  if (cudaMalloc(&bindings[1], num_out*sizeof(float)) || !bindings[1]) {
    mats_log(MATS_ERROR, "Failed cudaMalloc allocation for output.");
    goto finish;
  }

  // Extract channel data into TRT input buffer.
  // std::cerr << "nclass: " << nclass << std::endl;
  // std::cerr << "nchan: " << nchan_ << std::endl;
  // std::cerr << "in_size: " << num_in << std::endl;
  // std::cerr << "buffer size: " << img_buff.size() << std::endl;
  input.data("IMG-R")->size(&nr, &nc);
  xfactor = static_cast<float>(nc) / static_cast<float>(img_nc_);
  yfactor = static_cast<float>(nr) / static_cast<float>(img_nr_);

  // std::cerr << "xfactor: " << xfactor << std::endl;
  // std::cerr << "yfactor: " << yfactor << std::endl;
  // std::cerr << "input scaling: [" << nr << "x" << nc << "] -> [" << img_nr_
  //     << "x" << img_nc_ << "]\n";

  for (size_t ch=0; ch < channels_.size(); ch++) {
    std::vector<float> buffer(nr*nc);
    mats::mats_data_copy(*input.data(channels_[ch].c_str()), buffer.data(),
        (float *) 0);
    mats::inplace_transpose(nc, nr, buffer.data());
    mats::img_resize(nr, nc, buffer.data(), img_nr_, img_nc_,
        &img_buff[ch*img_nr_*img_nc_]);
    mats::inplace_transpose(img_nr_, img_nc_, &img_buff[ch*img_nr_*img_nc_]);
    // std::cerr << channels_[ch] << "(" << nr << ", " << nc << ") -> ("
    //     << img_nr_ << ", " << img_nc_ << ")\n";

    #ifdef DETONNX_DEBUG
    dims[0] = nr; dims[1] = nc;
    mats::h5_create_array(fid, channels_[ch].c_str(), dims, buffer.data());
    #endif
  }

  #ifdef DETONNX_DEBUG
  dims3[0] = channels_.size(); dims3[1] = img_nc_; dims3[2] = img_nr_;
  mats::h5_create_array(fid, "img", dims3, img_buff.data());
  #endif

  if (cudaMemcpyAsync(bindings[0], &img_buff[0], num_in*sizeof(float),
      cudaMemcpyHostToDevice, stream)) {
    mats_log(MATS_ERROR, "Failed TensorRT network execution.");
    goto finish;
  }

  #ifdef TRT8_4
  if (!context->enqueueV2(bindings, stream, 0)) {
    mats_log(MATS_ERROR, "Failed TensorRT network execution.");
    goto finish;
  }
  #else
  context->setTensorAddress("images", bindings[0]);
  context->setTensorAddress("output0", bindings[1]);

  // Execute
  if (!context->enqueueV3(stream)) {
    mats_log(MATS_ERROR, "Failed TensorRT network execution.");
    goto finish;
  }
  #endif

  if (cudaMemcpyAsync(&results[0], bindings[1], num_out*sizeof(float),
      cudaMemcpyDeviceToHost, stream)) {
    mats_log(MATS_ERROR, "Error reported with device->host copy.")
    goto finish;
  }

  #ifdef DETONNX_DEBUG
  dims[0] = ndet_; dims[1] = nfeat_;
  mats::h5_create_array(fid, "output", dims, results.data());
  #endif

  // std::cerr << ndet_ << "x" << nfeat_ << std::endl;

  // Non-Maximum Suppression
  mats::inplace_transpose(ndet_, nfeat_, results.data());

  rptr = results.data();
  for (size_t k=0; k < ndet_; k++) {
    Detection d(rptr, nfeat_, yolov_);
    rptr += nfeat_;
    if (d.score() < thresh_) {
      continue;
    }
    dets.push_back(d);
  }
  // std::cerr << "Raw detections: " << dets.size() << std::endl;

  if (nms_ > 0.0)
    nms(dets, nms_);
  // std::cerr << "NMS detections: " << dets.size() << std::endl;

  for (size_t k=0; k < dets.size(); k++) {
    mats::MATS_contact con;
    mats::MATS_ecdata ecd;
    std::vector<double> feat(nclass);
    std::vector<double> pos(4);

    // std::cerr << "[" << k << "] " << dets[k].x() << " " << dets[k].y() << " "
    //     << dets[k].width() << " " << dets[k].height() << " " << dets[k].score()
    //     << std::endl;

    ecd.setDetscore(dets[k].score());
    pos[0] = dets[k].x() * xfactor;
    pos[1] = dets[k].y() * yfactor;
    pos[2] = dets[k].width() * xfactor;
    pos[3] = dets[k].height() * yfactor;
    for (size_t j=0; j < nclass; j++)
      feat[j] = dets[k].feature(j);

    con.addFeature("BoundingBox", pos);
    con.addFeature("detYoloOnnx", feat);
    con.setX(static_cast<size_t>(pos[0]));
    con.setY(static_cast<size_t>(pos[1]));
    contacts.push_back(con);
    ecdata.push_back(ecd);
  }
  // std::cerr << contacts.size() << " contacts found.\n";

  finish:
  if (bindings[0])
    cudaFree(bindings[0]);
  if (bindings[1])
    cudaFree(bindings[1]);
  delete context;
  cudaStreamDestroy(stream);

  #ifdef DETONNX_DEBUG
  mats::mats_H5Fclose(fid);
  #endif

  // std::cerr << "[/detYoloOnnx::detect]\n";
  return 0;
}


int
detYoloOnnx::load_engine_(const std::string fn) {
  std::ifstream ifs(fn, std::ios::binary | std::ifstream::in);
  // nvinfer1::IRuntime *runtime = 0;
  char *buffer = 0;
  size_t buf_size = 0;  // Size of engine file header
  void *ser_mem = 0;
  size_t ser_mem_size = 0;
  int status = 0;

  // runtime = nvinfer1::createInferRuntime(gLogger);
  // if (!runtime) {
  //   mats_log(MATS_ERROR, "Failed to create TensorRT runtime.");
  //   status = 1;
  //   goto finish;
  // }

  // Release any existing engine
  if (engine_) {
    nvinfer1::ICudaEngine *engine;
    engine = static_cast<nvinfer1::ICudaEngine*>(engine_);
    mats_log(MATS_MSG, "Releasing existing engine.");
    delete engine;
    engine_ = 0;
  }

  // Figure out size of engine, so we can load it into memory.
  ifs.seekg(0, std::ios::end);
  ser_mem_size = static_cast<int>(ifs.tellg()) - static_cast<int>(buf_size);
  ifs.seekg(buf_size, std::ios::beg);
  ser_mem = malloc(ser_mem_size);
  if (!ser_mem) {
    mats_log(MATS_ERROR, "Failed allocation of memory for serial engine.");
    status = 1;
    goto finish;
  }
  ifs.read(static_cast<char*>(ser_mem), ser_mem_size);

  engine_ = static_cast<nvinfer1::IRuntime*>(runtime_)->deserializeCudaEngine(ser_mem, ser_mem_size);
  // engine_ = runtime->deserializeCudaEngine(ser_mem, ser_mem_size);
  if (!engine_) {
    mats_log(MATS_WARN, "Unable to load engine file.");
  }

finish:
  if (ser_mem) free(ser_mem);
  // if (runtime) delete runtime;
  if (buffer) delete[] buffer;
  ifs.close();
  return status;
}


int
detYoloOnnx::engine_io_() {
  nvinfer1::ICudaEngine *engine = static_cast<nvinfer1::ICudaEngine *>(engine_);

  #ifdef TRT8_4
  std::vector< nvinfer1::Dims > input_dims;
  std::vector< nvinfer1::Dims > output_dims;

  for (size_t i = 0; i < engine->getNbBindings(); ++i) {
    // auto binding_size = getSizeByDim(engine->getBindingDimensions(i)) * batch_size * sizeof(float);
    // cudaMalloc(&buffers[i], binding_size);
    if (engine->bindingIsInput(i)) {
      // std::cerr << "  - Binding[" << i << "] is an input.\n";
      input_dims.emplace_back(engine->getBindingDimensions(i));
    } else {
      // std::cerr << "  - Binding[" << i << "] is an output (";
      // for (size_t k = 0; k < engine->getBindingDimensions(i).nbDims; k++)
      //   std::cerr << engine->getBindingDimensions(i).d[k] << ", ";
      // std::cerr << ")\n";
      output_dims.emplace_back(engine->getBindingDimensions(i));
    }
  }

  nchan_ = input_dims[0].d[1];
  img_nr_ = input_dims[0].d[2];
  img_nc_ = input_dims[0].d[3];

  ndet_ = output_dims[0].d[2];
  nfeat_ = output_dims[0].d[1];
  #else
  nvinfer1::Dims input_dims;
  nvinfer1::Dims output_dims;

  input_dims = engine->getTensorShape("images");
  output_dims = engine->getTensorShape("output0");

  if (input_dims.nbDims > 4)
    mats_log(MATS_WARN, "More than 4 input dims detected.");
  nchan_ = input_dims.d[1];
  img_nr_ = input_dims.d[2];
  img_nc_ = input_dims.d[3];

  if (output_dims.nbDims > 3)
    mats_log(MATS_WARN, "More than 3 output dims detected.");
  ndet_ = output_dims.d[2];
  nfeat_ = output_dims.d[1];
  #endif

  return 0;
}
