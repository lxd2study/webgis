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
    terrain: Cesium.Terrain.fromWorldTerrain(), // 开启全球地形
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
  // 飞到一个初始位置，比如北京
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(116.39, 39.9, 10000),
    orientation: {
      heading: 0,
      pitch: -Cesium.Math.PI_OVER_TWO,
      roll: 0,
    },
  });
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
</style>
