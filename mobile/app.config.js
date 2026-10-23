const base=require('./app.json').expo;
module.exports=()=>({...base,
 icon:'./assets/icon.png',
 splash:{image:'./assets/splash.png',resizeMode:'contain',backgroundColor:'#f4f7f3'},
 ios:{...base.ios,infoPlist:{...base.ios.infoPlist,NSLocalNetworkUsageDescription:'Connect to the institutional attendance API on your local network.',
  NSAppTransportSecurity:process.env.SPVS_DEV_HTTP==='1'?{NSAllowsArbitraryLoads:true}:{NSAllowsLocalNetworking:true}}},
 android:{...base.android,adaptiveIcon:{foregroundImage:'./assets/adaptive-icon.png',backgroundColor:'#17695b'}},
 plugins:[...base.plugins,'./plugins/withSpvs'],
});
