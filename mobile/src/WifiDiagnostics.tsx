import React,{useState} from 'react';
import {ActivityIndicator,Pressable,StyleSheet,Text,View} from 'react-native';
import * as Location from 'expo-location';
import {collectWifi} from './signals';
import type {WifiResult} from './contracts';

export function WifiDiagnostics(){
 const [result,setResult]=useState<WifiResult|null>(null);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 async function scan(){
  setBusy(true);setResult(null);setError('');
  try{
   if((await Location.requestForegroundPermissionsAsync()).status!=='granted')throw new Error('Allow location access to check nearby Wi-Fi.');
   if(!await Location.hasServicesEnabledAsync())throw new Error('Turn on Location Services, then try again.');
   setResult(await collectWifi());
  }catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}
 }
 return <View style={styles.card}>
  <Text style={styles.title}>Wi-Fi setup check</Text>
  <Text style={styles.body}>Check the network evidence this phone can collect before attempting attendance. This check stays on your phone and does not record attendance.</Text>
  <Pressable accessibilityRole="button" accessibilityState={{disabled:busy}} disabled={busy} onPress={scan} style={styles.button}>
   <Text style={styles.buttonText}>{busy?'Checking Wi-Fi…':'Check Wi-Fi'}</Text>
  </Pressable>
  {busy&&<ActivityIndicator color="#17695b"/>}
  {!!error&&<Text accessibilityRole="alert" style={styles.body}>{error}</Text>}
  {result?.status==='available'&&<>
   <Text style={styles.body}>{result.source==='scan'?`${result.observations.length} nearby access points detected.`:'Connected access point detected.'}</Text>
   <Text style={styles.body}>An administrator must confirm which access points belong to the classroom before adding references. An access-point ID is different from your phone’s Wi-Fi address.</Text>
   {result.currentBssid&&<Text selectable style={styles.reading}>{result.currentBssid}</Text>}
   {result.observations.map(w=><Text selectable key={w.bssid} style={styles.reading}>{w.bssid} · {w.rssi} dBm</Text>)}
  </>}
  {result?.status==='permission_denied'&&<Text style={styles.body}>Enable Precise Location for SPVS in system settings, then try again.</Text>}
  {result?.status==='unsupported'&&<Text style={styles.body}>Install the SPVS native development build to use Wi-Fi checks.</Text>}
  {result?.status==='unavailable'&&<Text style={styles.body}>No recent Wi-Fi evidence was available. Check Wi-Fi and Precise Location. Android may limit repeated scans; wait before trying again. iPhone builds also need the Wi-Fi Information capability.</Text>}
 </View>;
}
const styles=StyleSheet.create({
 card:{backgroundColor:'#fff',padding:20,borderRadius:14,borderWidth:1,borderColor:'#dfe8dc',gap:12},
 title:{fontSize:17,fontWeight:'600',color:'#204735'},body:{fontSize:14,lineHeight:23,color:'#526c59'},
 button:{padding:14,backgroundColor:'#17695b',borderRadius:8,alignItems:'center'},
 buttonText:{color:'#fff',fontSize:13,fontWeight:'600'},reading:{fontSize:13,color:'#173b32'},
});
