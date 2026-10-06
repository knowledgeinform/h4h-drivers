# TODO

## Current milestone
- [x] Create initial repo structure
- [x] Build minimal end-to-end pipeline
- [x] Open Mac built-in camera
- [x] Load local YOLO model
- [x] Run inference on live frames
- [x] Extract detections
- [x] Serialize detections to JSON
- [x] Send JSON to mock sink
- [x] Confirm offline/local runtime works for prototype

## Immediate next steps
- [x] Finalize mapper filtering by `classes_of_interest`
- [x] Set `sports ball` as the current test object
- [x] Verify only `sports ball` detections are emitted
- [x] Save sample JSON outputs for reference
- [ ] Update detection JSON schema to fit XATR/COT output schema

## Validation and robustness
- [ ] Add startup validation for config file
- [ ] Add startup validation for model file
- [ ] Validate source type and source value
- [ ] Validate sink type
- [ ] Handle zero-detection frames cleanly
- [ ] Add clearer logging at startup and shutdown

## Mock sink improvements
- [ ] Add option to write JSON output to file
- [ ] Add per-frame summary logging
- [ ] Add message counter for debugging

## Replay/test workflow
- [ ] Add video replay mode using saved local video
- [ ] Add sample test video under `data/samples/`
- [ ] Save representative JSON output under `data/outputs/`
- [ ] Create a simple regression test for replay mode

## Testing
- [ ] Add `test_mapper.py`
- [ ] Add `test_serializer.py`
- [ ] Add a basic pipeline smoke test
- [ ] Test with no detections present
- [ ] Test with invalid model path
- [ ] Test with invalid source configuration

## RTSP support
- [ ] Test RTSP input path
- [ ] Add RTSP reconnect logic
- [ ] Add frame timeout handling
- [ ] Add useful RTSP error messages

## Docker
- [ ] Create Dockerfile
- [ ] Verify container runs with local video file
- [ ] Verify container runs with RTSP source
- [ ] Mount config and model paths cleanly
- [ ] Document container run commands
- [ ] Confirm runtime remains self-contained/offline

## Offline/self-contained requirements
- [ ] Ensure no runtime downloads
- [ ] Ensure model loads only from local path
- [ ] Ensure dependencies are packaged locally
- [ ] Keep logs and outputs local
- [ ] Test with internet disconnected

## Framework integration
- [ ] Replace mock sink with real framework adapter
- [ ] Confirm framework accepts JSON payload format
- [ ] Add error handling around framework submission
- [ ] Define behavior for sink failures
- [ ] Add retry/backoff only if needed

## Orin preparation
- [ ] Create `orin.yaml`
- [ ] Keep source/detector/sink interfaces hardware-agnostic
- [ ] Test with external camera on target hardware
- [ ] Benchmark inference performance on Orin
- [ ] Tune model/runtime only after baseline works

## Future model work
- [ ] Continue using `sports ball` as test object for pipeline validation
- [ ] Collect images/data for traffic cones
- [ ] Train or fine-tune custom traffic-cone detector
- [ ] Swap custom model into existing pipeline
- [ ] Validate cone detections through JSON/framework path

## Documentation
- [ ] Add setup steps to `README.md`
- [ ] Add local run instructions
- [ ] Add config documentation
- [ ] Add model placement instructions
- [ ] Add Docker usage examples
- [ ] Document known limitations on macOS + Docker camera access