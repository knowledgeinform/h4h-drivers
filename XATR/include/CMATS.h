/**
 * @file
 * @brief File contains high-level classes and routines for concurrent ATR
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
#ifndef SRC_CMATS_H_
#define SRC_CMATS_H_

#ifdef MATS_THREADING
#include <pthread.h>
#endif

#include <list>
#include <queue>

#include "MATS.h"


namespace mats {

class CMATS_atr_task;


/**
 * Base CMATS_atr_task data container. Used internally to store CMATS_atr_task
 * information. This class is not intended to be used outside of
 * CMATS_atr_task.
 */
class MATS_LIB CMATS_atr_task_base {
 public:
  std::string filename;
  MATS_input input;
  MATS_contact_list contacts;
  MATS_ecdata_list ecdata;
  int status;
  int seq_number;

 private:
  friend class CMATS_atr_task;
  unsigned count_;
  CMATS_atr_task_base();  // Prevent users from directly using
};


/**
 * Main CMATS_atr_task data structure
 */
class MATS_LIB CMATS_atr_task {
 public:
  /**
   * Construct an empty CMATS_atr_task.
   */
  CMATS_atr_task();

  /**
   * Copy constructor for CMATS_atr_task.
   *
   * @param[in] task CMATS_atr_task to be copied.
   *
   * @warning This does not actually create a new copy of the task; instead,
   * it adds to the reference count of the existing task. To create a new copy,
   * use the copy() method.
   */
  CMATS_atr_task(const CMATS_atr_task& task);

  /**
   * CMATS_atr_task destructor
   */
  ~CMATS_atr_task();

  /**
   * Assignment operator for CMATS_atr_task.
   *
   * @param[in] task CMATS_atr_task value to assign.
   *
   * @warning This does not actually create a new copy of the task; instead,
   * it adds to the reference count of the existing task. To create a new copy,
   * use the copy() method.
   */
  CMATS_atr_task& operator=(const CMATS_atr_task& task);

  /**
   * Copy an existing CMATS_atr_task.
   *
   * @param[in] task The task to be copied.
   *
   * @warning This method copies the entire task, including the MATS_input it
   * contains. This can be an expensive operation. It should only be used if
   * a separate copy is required.
   */
  void copy(const CMATS_atr_task& task);

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

 private:
  CMATS_atr_task_base* p_;
};


#ifdef MATS_THREADING

class MATS_LIB CMATS_Thread {
 public:
  CMATS_Thread();
  virtual ~CMATS_Thread();
  virtual void run() = 0;
  int start();  // start or restart the thread (call the run() method)
  int join();  // wait for the thread to finish

 private:
  pthread_t thread_;
  bool created_;  /**< Has thread been created and not yet joined? */
  bool running_;  /**< Is thread still running? */
  pthread_mutex_t thread_lock_;  /**< Lock for thread_ and created_. */
  static void* cmats_thread_run(void* th);
};


class CMATS;
class CMATS_Manager;


/**
 * A Worker is a MATS object that can be assigned tasks and execute them in
 * a separate thread. A Worker needs a Manager assigned so that it can return
 * task results.
 */
class MATS_LIB CMATS_Worker : public CMATS_Thread {
 public:
  CMATS_Worker();
  explicit CMATS_Worker(CMATS_Manager* mngr);
  ~CMATS_Worker();

  int configure(const char* sensor, const char* uuid = NULL);
  int options(const MATS_struct& opt);
  int addGroundtruth(std::vector<MATS_groundtruth> gt);
  int archive(bool enabled, const char* saveLocation);

  void run();
  int assignTask(CMATS_atr_task& job);
  int status();  // return 1 for working, 0 for idle, -1 for tasked but not working.
  void quit();

 private:
  void init_();  /**< Initialize everything to default value. */

  bool quit_;  /**< Flag signaling if worker thread should terminate. */
  bool tasked_;  /**< Flag indicating if a task has been assigned. */
  bool processing_;  /**< Flag indicating worker thread is running. */
  CMATS_Manager* mngr_;  /**< Pointer to manager for results reporting. */
  CMATS_atr_task job_;  /**< Current assigned task. */
  MATS mats_;
  pthread_mutex_t config_lock_;  /**< Lock for configuration. */
};


/**
 * Defines a task manager for CMATS. The manager collects tasks to be processed
 * and completed tasks.
 */
class MATS_LIB CMATS_Manager : public CMATS_Thread {
 public:
  explicit CMATS_Manager();
  ~CMATS_Manager();

  int configure(const char* sensor, const char* uuid = NULL);
  int options(const MATS_struct& opt);
  int addGroundtruth(std::vector<MATS_groundtruth>& gt);
  int archive(bool enabled, const char* saveLocation);

  size_t jobs() const;  // Number of jobs waiting to be processed.
  size_t completed() const;  // Number of completed jobs not retrieved.

  void run();
  int status();  // return 1 for busy, 0 for idle, -1 for stopped, -2 for failure.
  void quit();  // tell manager and workers to quit
  void joinWorkers();  // wait for worker threads to finish

  int add(CMATS_atr_task& job);  // add a new task (increment seq number), returns 0 on success
  int getTask(CMATS_atr_task& job);  // request a task from the manager, returns 0 on success

  int completed(CMATS_atr_task& job);  // notify manager of completed job, returns 0 on success
  int result(CMATS_atr_task& job);  // retrieve a job result if available, returns 1 on success

 private:
  int workerStatus_();  // return 1 for working, 0 for not working

  bool quit_;
  int status_;
  size_t wait_time_;
  int seq_number_;
  MATS_cfg cfgmngr_;

  std::vector<CMATS_Worker*> worker_;
  std::queue<CMATS_atr_task> job_;
  std::queue<CMATS_atr_task> completed_;

  mutable pthread_mutex_t job_lock_;
  mutable pthread_mutex_t completed_lock_;
  mutable pthread_mutex_t config_lock_;
};

#endif


class MATS_LIB CMATS {
 public:
  CMATS();
  ~CMATS();

  /**
   * Initialize MATS. This should be called first to setup MATS package manager
   * and processing threads.
   *
   * @return Returns 0 on success.
   */
  int init();

  /**
   * Returns the current version of %MATS.
   */
  const char* version() const;

  /**
   * Returns a copy of current ATR configuration.
   *
   * @return ATR current configuration
   */
  mats::ATR_Configuration configuration() const;

  /**
   * Creates and configures a processing stream for the data.  Configuration
   * information is chosen based on the given sensor and configuration UUID.
   *
   * @param[in] sensor Name of the sensor.
   * @param[in] uuid (Optional) UUID of the desired configuration.  If none is
   * provided, the first selected configuration is used instead.
   *
   * @return Returns 0 on success.
   */
  int configure(const char* sensor, const char* uuid = NULL);

  /**
   * Set advanced options for processing. CMATS should be configured first
   * to ensure that options persist or are correctly applied.
   *
   * @param[in] opt Options structure containing option and value pairs.
   *
   * @return Returns 0 on success.
   */
  int options(const MATS_struct& opt);

  /**
   * Add runtime groundtruth information to be applied to generated contacts.
   *
   * @param[in,out] gt Vector of known contact locations (will be cleared upon
   * successful completion).
   *
   * @return Returns 0 on success.
   */
  int addGroundtruth(std::vector<MATS_groundtruth>& gt);

  /**
   * Enable/Disable result archiving.
   *
   * @param[in] enabled Flag to enable/disable archiving.
   * @param[in] saveLocation File system location to save archives.
   *
   * @return Returns 0 on success.
   */
  int archive(bool enabled, const char* saveLocation);

  /**
   * Imports data from file into MATS_input structure, runs %MATS ATR
   * on that structure, and produces MATS_contact and MATS_ecdata vectors
   * of results. Results are retrieved by a call to the result function.
   *
   * @param[in] filename Filename of data file.
   *
   * @return Returns 0 if the job is successfully sent for processing.
   */
  int atr(const char* filename);

  /**
   * Run %MATS ATR on a specified task structure. Results are retrieved by a
   * call to the result function.
   *
   * If the task filename has been set, the ATR will be run on that file. If
   * the task filename is not set, the task input will be used instead.
   *
   * @param[in] job The task structure to be processed.
   *
   * @return Returns 0 if the job is successfully sent for processing.
   */
  int atr(CMATS_atr_task& job);

  /**
   * Retrieves ATR results if available.
   *
   * @param[out] job The results from a completed task, if available.
   *
   * @return Returns 1 on successful retrieval of results, otherwise 0.
   */
  int result(CMATS_atr_task& job);

  /**
   * Returns the status of processing.
   *
   * @return Returns 1 for busy, 0 for idle, -1 for stopped, and -2 for failure.
   */
  int status();

  /**
   * Returns the number of jobs/tasks that are queued for processing.
   *
   * @return Number of jobs waiting to be processed.
   */
  size_t jobs() const;

  /**
   * Returns the number of completed jobs/tasks that have not been retrieved.
   *
   * @return Number of jobs not retrieved.
   */
  size_t completed() const;

 private:
  #ifdef MATS_THREADING
  int start_mngr_();
  CMATS_Manager* mngr_;
  #endif

  MATS_cfg cfgmngr_;
  MATS primary_worker_;
  std::queue<CMATS_atr_task> completed_;
  bool configured_;

  MATS_struct opt_;
  std::vector<MATS_groundtruth> gt_;
  bool archiving_;
  std::string arc_loc_;
};

}  // namespace mats

#endif  // SRC_CMATS_H_
