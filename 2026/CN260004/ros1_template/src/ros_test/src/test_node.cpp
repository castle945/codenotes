#include <ros/ros.h>
#include <glog/logging.h>
#include <yaml-cpp/yaml.h>

#include <ros_msgs/subscriber/msg_subscriber.h>
#include <ros_msgs/publisher/cloud_vec_publisher.h>
#include <pcl_conversions/pcl_conversions.h>
#include <deque>

#include <pcl/io/pcd_io.h>
#include <pcl/point_cloud.h>

using namespace std;
using namespace pcl;

typedef MsgSubscriber<sensor_msgs::PointCloud2> CloudSubscriber;

std::string WORK_SPACE_PATH;
std::shared_ptr<CloudSubscriber> cloud_lidar_sub_ptr;
std::deque<sensor_msgs::PointCloud2> cloud_data_buf;
YAML::Node config_node;

int main(int argc, char* argv[])
{
  ros::init(argc, argv, "test_node");
  ros::NodeHandle nh;

  nh.param<string>("ROS_TEST_WS", WORK_SPACE_PATH, "~/");
  google::InitGoogleLogging(argv[0]);
  FLAGS_log_dir = WORK_SPACE_PATH + "/log";
  FLAGS_alsologtostderr = 1;

  // 配置文件与参数
  std::string config_file_path = WORK_SPACE_PATH + "/config/test.yaml";
  config_node = YAML::LoadFile(config_file_path);
  string cloud_frame = config_node["cloud_frame"].as<string>();
  string cloud_topic = config_node["cloud_topic"].as<string>();
  int total_merge_num = config_node["total_merge_num"].as<int>();

  // 输入
  cloud_lidar_sub_ptr = std::shared_ptr<CloudSubscriber>(new CloudSubscriber(nh, cloud_topic, 100));

  // 可视化
  std::shared_ptr<CloudVecPublisher> cloud_view_pub_ptr = std::shared_ptr<CloudVecPublisher>(new CloudVecPublisher(nh, "/cloud_view", cloud_frame, 100));
  std::vector<PointCloudT::Ptr> cloud_vec_view;
  // 处理

  ros::Rate rate(10);
  while (ros::ok())
  {
    ros::spinOnce();

    cloud_lidar_sub_ptr->ParseData(cloud_data_buf);

    while (cloud_data_buf.size() > total_merge_num)
    {
      // 循环变量初始化
      cloud_vec_view.clear();
      int cur_merge_num = 0;

      // 取数据
      PointCloudT::Ptr cloud_src(new PointCloudT);
      PointCloudT::Ptr cloud_merge(new PointCloudT);
      while (cur_merge_num++ < total_merge_num)
      {
        pcl::fromROSMsg(cloud_data_buf.front(), *cloud_src);
        cloud_data_buf.pop_front();
        *cloud_merge += *cloud_src;
      }

      cloud_vec_view.push_back(cloud_merge);
      cloud_view_pub_ptr->Publish(cloud_vec_view, ros::Time::now());
    }

    rate.sleep();
  }
}