const {withEntitlementsPlist,withPodfileProperties,withAndroidManifest}=require('expo/config-plugins');
module.exports=function withSpvs(config){
 config=withPodfileProperties(config,c=>{c.modResults['ios.deploymentTarget']='16.4';return c});
 config=withEntitlementsPlist(config,c=>{
  c.modResults['com.apple.developer.networking.wifi-info']=true;
  const environment=process.env.SPVS_APP_ATTEST_ENV;
  if(environment){if(!['development','production'].includes(environment))throw new Error('Invalid SPVS_APP_ATTEST_ENV');c.modResults['com.apple.developer.devicecheck.appattest-environment']=environment}
  return c;
 });
 return withAndroidManifest(config,c=>{const application=c.modResults.manifest.application?.[0];if(application){application.$['android:allowBackup']='false';application.$['android:usesCleartextTraffic']=process.env.SPVS_DEV_HTTP==='1'?'true':'false'}return c});
};
