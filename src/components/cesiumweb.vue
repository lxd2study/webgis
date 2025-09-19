<template>
  <div id="cesium-container"></div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css"; // 引入样式
declare global {
  interface Window {
    viewer: any;
  }
}
// TODO: 替换为你自己的 Token
Cesium.Ion.defaultAccessToken =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmMmY3MWFlMS0xNmJkLTQ4ZDktYjViOC1kMmRhZDY5YWFiYTUiLCJpZCI6MTUxMzE1LCJpYXQiOjE2OTI1MzUwNTF9.EHjYEmZ30sa36HF5ZiuonIIVDSkJZI1kh6qDrpd1z0I";

onMounted(() => {
  const viewer = new Cesium.Viewer("cesium-container", {
    //关闭部分默认UI
    animation: false, // 关闭动画控制
    timeline: false, // 关闭时间线
    fullscreenButton: false, // 关闭全屏按钮
    vrButton: false, // 关闭VR按钮
    geocoder: false, // 关闭地名查找
    homeButton: false, // 关闭Home按钮
    infoBox: false, // 关闭点击要素之后显示的信息
    selectionIndicator: false, // 关闭点击要素之后显示的指示器
    navigationHelpButton: false, // 关闭帮助按钮
    sceneModePicker: false, // 关闭2D/3D切换按钮
    baseLayerPicker: false, // 关闭底图切换按钮
  });
  viewer.scene.debugShowFramesPerSecond = true; // 顺带显示 FPS
  //全局变量viewer，方便其他组件调用
  window.viewer = viewer;
  //加载天地图
  const tdtImg = new Cesium.WebMapTileServiceImageryProvider({
    // 服务URL地址，使用天地图提供的WMTS服务
    url: `https://t0.tianditu.gov.cn/img_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=img&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd`,
    // 图层名称
    layer: "tdtImgLayer",
    // 图层样式
    style: "default",
    // 图片格式
    format: "image/jpeg",
    // 瓦片矩阵集ID，使用Google Maps兼容的坐标系
    tileMatrixSetID: "GoogleMapsCompatible",
    // 最大缩放级别
    maximumLevel: 18,
  });
  viewer.imageryLayers.addImageryProvider(tdtImg);
});
</script>

<style>
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

#app {
  width: 100%;
  height: 100%;
}

#cesium-container {
  width: 100%;
  height: 100%;
}

.cesium-viewer-bottom {
  display: none !important;
}
</style>
