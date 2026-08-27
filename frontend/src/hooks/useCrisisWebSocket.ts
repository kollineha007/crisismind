import {useEffect} from 'react';
import {connect,getState} from '../services/api';
export function useCrisisWebSocket(setState:(state:any)=>void){useEffect(()=>{let socket:WebSocket|undefined;let timer:number|undefined;const open=()=>{socket=connect(()=>getState().then(setState).catch(()=>{}));socket.onclose=()=>{timer=window.setTimeout(open,2000)}};open();return()=>{if(timer)window.clearTimeout(timer);socket?.close()};},[setState]);}
