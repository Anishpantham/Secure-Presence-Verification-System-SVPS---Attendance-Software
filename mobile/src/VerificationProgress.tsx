import React from 'react';
import {View,Text} from 'react-native';
export function VerificationProgress({step}:{step:number}){
 return <View accessibilityLabel="Verification progress" style={{flexDirection:'row',flexWrap:'wrap',gap:6}}>
  {['Eligibility','Identity','Presence','Decision'].map((label,index)=><View key={label} style={{padding:8,borderRadius:8,backgroundColor:step>=index+1?'#cce6db':'#e3e9e4'}}>
   <Text accessibilityLabel={`${label}: ${step>index+1?'completed':step===index+1?'current':'waiting'}`} style={{color:'#173b32',fontSize:12}}>{index+1} · {label}</Text>
  </View>)}
 </View>;
}
