# Openmv-Image-Analysis
A tool use to analyse openmv-image.

采用pyqt5、opencv编写，opencv版本：4.2.0

本项目可帮助你脱离ide进行图像的分析，roi的选取，lab值的分析。

分析图像时需要将image_transfer_jpg_streaming_as_the_remote_device_for_your_computer.py保存为main.py至openmv的根目录当中。

若未将 rpc_image_transfer_jpg_streaming_as_the_controller_device.py编译生成transfer_jpg_streaming.exe与分析工具放至同一目录，请直接运行rpc_image_transfer_jpg_streaming_as_the_controller_device.py，随后在该脚本中连接openmv，无需再在分析工具中连接openmv。


















