@REM 비행정보 아이디
set param1=%1
if not defined param1 set param1=default_flight_id

@REM 인풋 파일 혹은 폴더 경로
set param2=%2
if not defined param2 set param2=.

@REM 결과 저장 폴더 경로
set param3=%3
if not defined param3 set param3=runs/detect

@REM 동영상 FPS
set param4=%4
if not defined param4 set param4=5

set /a stride=60 / param4

call conda activate yolo

call python convert_srt.py %param2%

call python detect_and_track.py --weights 231018_e6e4_best.pt --conf 0.25 --img-size 1280 --vid-stride %stride% --project %param3% --name %param1% --no-trace --save-txt --save-bbox-dim --save-with-object-id --source %param2%

@REM 프로그램이 끝나고 난 후 HTTP POST 요청 보내기
set "body=%param1%"
set "url=http://localhost:8888/link/batchYfinish"
set "contentType=text/plain"

curl -X POST -H "Content-Type: %contentType%" --data-raw "%body%" %url%

pause