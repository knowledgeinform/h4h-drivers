/**
 * @file
 * @brief File contains high-level classes and routines for asycronous ATR
 * processing.
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
#ifndef SRC_AMATS_H_
#define SRC_AMATS_H_

#include <thread>
#include <list>
#include <queue>
#include <atomic>
#include <mutex>

#include "MATS.h"

namespace mats {

class AMATS_task;


class MATS_LIB AMATS_task_base {
 public:
  std::string filename;
  MATS_input input;
  MATS_contact_list contacts;
  MATS_ecdata_list ecdata;
  int status;
  int seq_number;

 private:
  friend class AMATS_task;
  std::atomic<unsigned> count_;
  AMATS_task_base();  // Prevent users from directly using
};


class MATS_LIB AMATS_task {
 public:
  /**
   * Construct an empty AMATS_task.
   */
  AMATS_task();

  /**
   * Copy constructor for AMATS_task.
   *
   * @param[in] task AMATS_task to be copied.
   *
   * @warning This does not actually create a new copy of the task; instead,
   * it adds to the reference count of the existing task. To create a new copy,
   * use the copy() method.
   */
  AMATS_task(const AMATS_task& task);

  /**
   * AMATS_task destructor
   */
  ~AMATS_task();

  /**
   * Assignment operator for AMATS_task.
   *
   * @param[in] task AMATS_task value to assign.
   *
   * @warning This does not actually create a new copy of the task; instead,
   * it adds to the reference count of the existing task. To create a new copy,
   * use the copy() method.
   */
  AMATS_task& operator=(const AMATS_task& task);

  /**
   * Copy an existing AMATS_task.
   *
   * @param[in] task The task to be copied.
   *
   * @warning This method copies the entire task, including the MATS_input it
   * contains. This can be an expensive operation. It should only be used if
   * a separate copy is required.
   */
  void copy(const AMATS_task& task);

  /**
   * Returns the filename of the task.
   */
  const char* filename() const;

  /**
   * Set the filename of the task.
   *
   * @param[in] filename Filename string.
   */
  void setFilename(const char* filename);

  /**
   * Set the filename of the task.
   *
   * @param[in] filename Filename string.
   */
  void setFilename(const std::string& filename);

  /**
   * Returns a pointer to the input of the task.
   */
  MATS_input* input();

  /**
   * Returns a const pointer to the input of the task.
   */
  const MATS_input* input() const;

  /**
   * Returns a pointer to the contact list of the task.
   */
  MATS_contact_list* contacts();

  /**
   * Returns a const pointer to the contact list of the task.
   */
  const MATS_contact_list* contacts() const;

  /**
   * Returns a pointer to the ecdata list of the task.
   */
  MATS_ecdata_list* ecdata();

  /**
   * Returns a const pointer to the ecdata list of the task.
   */
  const MATS_ecdata_list* ecdata() const;

  /**
   * Returns task status.
   */
  int status() const;

  /**
   * Set task status.
   *
   * @param[in] status Status of task.
   */
  void setStatus(int status);

  /**
   * Returns sequence number of task.
   */
  int seqNumber() const;

  /**
   * Set sequence number of task.
   *
   * @param[in] seqNumber Sequence number of task.
   */
  void setSeqNumber(int seqNumber);

  std::mutex access;
 private:
  AMATS_task_base* p_;
};


typedef int (*results_callback)(mats::AMATS_task job);


class AMATS;
class AMATS_Manager;


class MATS_LIB AMATS_Worker {
 public:
  AMATS_Worker();
  explicit AMATS_Worker(AMATS_Manager* mngr);
  ~AMATS_Worker();

  int configure(const char* sensor, const char* uuid = NULL);
  int options(const MATS_struct& opt);
  int addGroundtruth(std::vector<MATS_groundtruth> gt);
  int archive(bool enabled, const char* saveLocation);

  void run();
  int assignTask(AMATS_task& job);

  int status();  // return 1 for working, 0 for idle, -1 for tasked but not working.
  int size();  // returns the number of queued tasks
  void quit();

 private:
  void init_();  /**< Initialize everything to default value. */
  void execute();
  void launch_();

  bool quit_;  /**< Flag signaling if worker thread should terminate. */
  bool processing_;  /**< Flag indicating worker thread is running. */
  std::atomic<bool> tasked_;
  std::atomic<int> size_;  /**< Task queue size. */
  std::atomic<size_t> head_;
  std::atomic<size_t> tail_;
  AMATS_Manager* mngr_;  /**< Pointer to manager for results reporting. */
  mats::AMATS_task task_;
  std::vector<AMATS_task> job_;  /**< Assigned tasks. */
  MATS mats_;
  std::thread *process_;
  std::mutex config_lock_;  /**< Lock for configuration. */
  // std::mutex job_lock_;
  std::mutex proc_lock_;
};


/**
 * Defines a task manager for AMATS. The manager collects tasks to be processed
 * and completed tasks.
 */
class MATS_LIB AMATS_Manager {
 public:
  explicit AMATS_Manager();
  ~AMATS_Manager();

  int configure(const char* sensor, const char* uuid = NULL);
  int options(const MATS_struct& opt);
  int addGroundtruth(std::vector<MATS_groundtruth>& gt);
  int archive(bool enabled, const char* saveLocation);

  size_t jobs() const;  // Number of jobs waiting to be processed.

  int status();  // return 1 for busy, 0 for idle, -1 for stopped, -2 for failure.
  void stop();  // Stops all processing.

  int add(AMATS_task& job);  // add a new task (increment seq number), returns 0 on success
  int getTask(AMATS_task& job);  // request a task from the manager, returns 0 on success

  int completed(AMATS_task& job);  // notify manager of completed job, returns 0 on success

  int addCallback(results_callback func);

 private:
  int workerStatus_();  // return 1 for working, 0 for not working

  int workerAllocation_(int num);

  bool quit_;
  int status_;
  std::atomic<int> ix_;  /**< Worker index. */
  std::atomic<int> seq_number_;
  MATS_cfg cfgmngr_;

  std::vector<AMATS_Worker*> worker_;

  std::mutex config_lock_;

  results_callback results_func_;
};

}  // namespace mats

#endif  // SRC_AMATS_H_
