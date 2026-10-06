/**
 * @file
 * @brief File contains the MATS_cx structure, which is used to export MATS
 * components.
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
#ifndef SRC_MATS_CX_H_
#define SRC_MATS_CX_H_

#include <stdint.h>

#include <string>
#include <vector>

#include "MATS_platform.h"
#include "MATS_cfg.h"


namespace mats {

const uint32_t MATSCX_ID[4] = {0x806A9FA2, 0xE1084F3E, 0x9F4EBAC2, 0x08E47226};
const uint32_t MATSCX_FRAG[4] = {0x806A9FA2, 0xE1084F3E, 0x9F4EBAC2, 0x08E47227};
const uint32_t MATSCX_TYPE_CFG = 0x00000000;
const uint32_t MATSCX_TYPE_ATRCFG = 0x00000001;
const uint32_t MATSCX_TYPE_DEP = 0x00000002;
const uint32_t MATSCX_TYPE_ARC = 0x00000003;
const uint32_t MATSCX_TYPE_ALG = 0x00000004;
const uint32_t MATSCX_TYPE_INS = 0x00000005;
const uint64_t MATSCX_MAX_FILE_SIZE = 1000000000;


/**
 * MATS_cx is a container for information to be exported
 */
class MATS_LIB MATS_cx {
 public:
  /**
   * MATS_cx default constructor.
   */
  MATS_cx();
  ~MATS_cx();

  /**
   * Adds configuration information for export.
   *
   * @param[in] cfgUUID UUID of the configuration to be added.
   * @param[in] arc Adds associated archive files to export.
   * @return Returns 0 on success.
   */
  int addConfig(const char *cfgUUID, bool arc = false);

  /**
   * Adds configuration algorithm modules for export.
   *
   * @param[in] cfgUUID UUID of the configuration with modules to be exported.
   * @return Returns 0 on success.
   */
  int addAlgorithm(const char *cfgUUID);

  /**
   * Exports added components.
   *
   * @param[in] filename Filename for export file
   * @param[out] exports File list of export files.
   * @param[in] progressBar Display progress bar.
   * @return Returns 0 on success.
   */
  int generate(std::string filename, std::vector<std::string> &exports,
      bool progressBar = false);

  /**
   * Extracts information from export file
   *
   * @param[in] filename Filename of export file to be imported.
   * @param force Enable overwrite of existing files
   * @param progressBar Display progress bar.
   * @return Returns 0 on success.
   */
  int import(std::string filename, bool force, bool progressBar = false);

 private:
  struct FileNode {
    uint32_t type;
    std::string name;
    std::string file;
    uint64_t size;
  };

  int add_node_(uint32_t type, const std::string &name);

  int update_path_(std::string fullname);
  int gen_node_(uint32_t type, const std::string &name, FileNode &node);
  std::string node_install_path_(FileNode &node);
  int export_file_(FILE *fid, FileNode &node);
  int extract_file_(FILE *fid, FileNode &node);
  FILE *open_frag_(uint32_t fragNum, const char *mode);
  int post_import_();

  std::string mcxPath_;
  std::string mcxBasename_;
  std::string exportPath_;
  std::string id_;
  std::string atrcfgName_;
  bool compression_;
  bool installer_;
  std::vector<FileNode> component_;
};


/**
 * Checks given file ID. Optionally returns version of MATSCX file.
 *
 * @param[in] id File ID to be checked.
 * @param[out] ver Version of matched MATSCX.
 * @return Returns zero if file ID matches a MATSCX. Returns one if file ID
 *         matches a MATSCX fragment.
 */
int
matscx_check_id(uint32_t *id, uint32_t *ver = 0);


/**
 * Checks filename for .matscxgz extension (indicating that it is compressed).
 *
 * @param[in] filename Filename of file to be checked.
 * @return Returns 1 if filename ends in .matscxgz. Returns zero otherwise.
 */
bool
matscx_check_compressed(const std::string &filename);


/**
 * Returns string type name of exported component.
 *
 * @param[in] cx_type MATS component export type ID.
 * @return Returns string name of component export type.
 */
std::string
matscx_type_name(uint32_t cx_type);

}  // namespace mats

#endif  // SRC_MATS_CX_H_
