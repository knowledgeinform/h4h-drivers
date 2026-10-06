/**
 * @file
 * @brief File contains macros, classes, and functions for handling messages.
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
#ifndef SRC_MATS_MESSAGE_H_
#define SRC_MATS_MESSAGE_H_

#include "MATS_struct.h"
#include "MATS_error.h"


/**
 * A macro for sending a MATS_message to the message handler. File, function,
 * and line number are filled in automatically.
 *
 * @param[in,out] msg The message to send, a MATS_message.
 *
 * @return Returns 0 on success.
 */
#define mats_message(msg) mats_msg_send(__FILE__, __FUNCTION__, __LINE__, \
    msg);


namespace mats {


/**
 * Message type.
 *
 * @li matsmsgGENERIC Generic message type.
 * @li matsmsgLOG Log message. Data fields include: "level" (MATS_error_action
 * enum).
 * @li matsmsgDIV Unprocessed data message from Data Integrity Verification
 * (DIV) code. Data fields include: "datafile" (string), "start_time" (double),
 * "stop_time" (double), and "status" (float). The "status" field ranges in
 * value from 0.0 (data not processed) to 1.0 (data processed, status OK).
 * @li matsmsgPERF Performance estimation message.
 */
enum MATS_msg_type {
  matsmsgGENERIC,
  matsmsgLOG,
  matsmsgDIV,
  matsmsgPERF
};


/**
 * The MATS_message class represents a generic message and serves as a base
 * class for more specific message types. It inherits from MATS_struct, which
 * allows the user to use MATS_struct methods to set and get any extra data
 * that the message requires.
 *
 * In general, you can copy-construct or assign a more specific message type
 * (derived from MATS_message) to a MATS_message. In this case, the
 * MATS_message "knows" what its message type is, even though it can't use
 * the more specific type's setter and getter methods.
 */
class MATS_LIB MATS_message : public MATS_struct {
 public:
  friend MATS_LIB void swap(MATS_message& a, MATS_message& b);

  /**
   * MATS_message constructor.
   *
   * @param[in] reason The message string or reason for the message.
   */
  MATS_message(const char* reason);

  /**
   * Set file, function, and line where message occurs.
   *
   * @param[in] file File (code) where message occurs.
   * @param[in] func Function where message occurs.
   * @param[in] line Line number where message occurs.
   *
   * @return Returns 0 on success.
   */
  int setMsgSource(const char* file, const char* func, int line);

  /**
   * Returns the name of the file where message occurs.
   */
  const char* file() const;

  /**
   * Returns the name of the function where message occurs.
   */
  const char* function() const;

  /**
   * Returns the line number where message occurs.
   */
  int line() const;

  /**
   * Set the message type.
   *
   * @param[in] type The message type.
   *
   * @return Returns 0 on success.
   */
  int setMsgType(MATS_msg_type type);

  /**
   * Returns the message type.
   */
  MATS_msg_type msgType() const;

  /**
   * Returns the message string / reason for the message.
   */
  const char* reason() const;

  /**
   * Display the contents of the MATS_message.
   *
   * @warning This method writes to stdout. Do not use this if stdout does
   * not exist, i.e., if there is no terminal interface.
   */
  void display() const;

 protected:
  MATS_msg_type type_;  /**< Message type. */

 private:
  std::string file_;  /**< File where the message occurs. */
  std::string function_;  /**< Function where the message occurs. */
  int line_;  /**< Line number where the message occurs. */
  std::string reason_;  /**< Message string / reason for message. */
};


/**
 * Exchange the values of two MATS_message objects.
 */
MATS_LIB void swap(MATS_message& a, MATS_message& b);


/**
 * The Msg_log class is derived from MATS_message. It is used for log messages.
 */
class MATS_LIB Msg_log : public MATS_message {
 public:
  /**
   * Msg_log constructor.
   *
   * @param[in] reason The message string or reason for the message.
   */
  Msg_log(const char* reason);

  /**
   * Construct a Msg_log by taking (moving) contents from a MATS_message.
   */
  Msg_log(MATS_message& msg);

  /**
   * Set the action level of the log message, i.e., warning, error, etc.
   *
   * @param[in] level The action level of the message.
   *
   * @return Returns 0 on success.
   */
  int setLevel(MATS_error_action level);

  /**
   * Get the action level of the log message, i.e., warning, error, etc.
   *
   * @return Returns the action level of the message.
   */
  MATS_error_action level() const;
};


/**
 * The Msg_div class is derived from MATS_message. It is used for
 * Data Integrity Verification (DIV) messages to indicate areas of
 * unprocessed data.
 */
class MATS_LIB Msg_div : public MATS_message {
 public:
  /**
   * Msg_div constructor.
   *
   * @param[in] reason The message string or reason for the message.
   */
  Msg_div(const char* reason);

  /**
   * Construct a Msg_div by taking (moving) contents from a MATS_message.
   */
  Msg_div(MATS_message& msg);

  /**
   * Set the name of the data file where the DIV message occurs.
   *
   * @param[in] datafile The data file.
   *
   * @return Returns 0 on success.
   */
  int setDatafile(const char* datafile);

  /**
   * Get the name of the data file where the DIV message occurs.
   *
   * @return Returns the data file C-string.
   *
   * @note If the datafile field doesn't exist, it will be created. This is to
   * avoid returning a null pointer.
   */
  const char* datafile();

  /**
   * Set the status for the DIV message region.
   *
   * @param[in] status The status, a float between 0.0 (data not processed) and
   * 1.0 (data processed, status OK).
   *
   * @return Returns 0 on success.
   */
  int setStatus(float status);

  /**
   * Get the status for the DIV message region.
   *
   * @return Returns the status, a float between 0.0 (data not processed) and
   * 1.0 (data processed, status OK).
   */
  float status() const;

  /**
   * Set the start time for the DIV message region. Time is defined as seconds
   * elapsed since 00:00 hours, Jan 1, 1970 UTC.
   *
   * @param[in] start_time The timestamp at the beginning of the region.
   *
   * @return Returns 0 on success.
   */
  int setStartTime(double start_time);

  /**
   * Get the start time for the DIV message region. Time is defined as seconds
   * elapsed since 00:00 hours, Jan 1, 1970 UTC.
   *
   * @return Returns the timestamp at the beginning of the region.
   */
  double startTime() const;

  /**
   * Set the stop time for the DIV message region. Time is defined as seconds
   * elapsed since 00:00 hours, Jan 1, 1970 UTC.
   *
   * @param[in] stop_time The timestamp at the end of the region.
   *
   * @return Returns 0 on success.
   */
  int setStopTime(double stop_time);

  /**
   * Get the stop time for the DIV message region. Time is defined as seconds
   * elapsed since 00:00 hours, Jan 1, 1970 UTC.
   *
   * @return Returns the timestamp at the end of the region.
   */
  double stopTime() const;
};


}  // namespace mats


/**
 * Get the status of the %MATS message handler.
 *
 * @return Returns true if the message handler is enabled; false otherwise.
 */
MATS_LIB bool
mats_msg_status();


/**
 * Enable or disable the %MATS message handler.
 *
 * @param[in] enable Set to true to enable the message handler; set to false
 * to disable it.
 *
 * @return Returns true if the message handler is enabled; false otherwise.
 *
 * @note The %MATS message handler is disabled by default.
 */
MATS_LIB bool
mats_msg_status(bool enable);


/**
 * Send a message to the %MATS message handler.
 *
 * The file, function, and line information will be added to the message before
 * sending.
 *
 * @param[in] file File (code) where message occurs.
 * @param[in] func Function where message occurs.
 * @param[in] line Line number where message occurs.
 * @param[in,out] msg The message to send.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_msg_send(const char* file, const char* func, int line,
    mats::MATS_message& msg);


/**
 * View all messages in the %MATS message handler without removing them from
 * the queue.
 *
 * @param[out] msgs A copy of all messages in the queue.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_msg_view(std::vector<mats::MATS_message>* msgs);


/**
 * View messages in the %MATS message handler, filtered by type, without
 * removing them from the queue.
 *
 * @param[in] type The type of message to view.
 * @param[out] msgs A copy of all messages of the requested type.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_msg_view(mats::MATS_msg_type type, std::vector<mats::MATS_message>* msgs);


/**
 * Clear the queue, and optionally retrieve all messages.
 *
 * @param[out] msgs (Optional) All messages in the queue right before it is
 * cleared. If left as NULL, the messages will be discarded.
 *
 * @return Returns 0 on success.
 */
MATS_LIB int
mats_msg_clear(std::vector<mats::MATS_message>* msgs = NULL);

#endif /* SRC_MATS_MESSAGE_H_ */
