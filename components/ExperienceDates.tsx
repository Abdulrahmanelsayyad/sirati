'use client';
import {useEffect,useId,useState} from 'react';
export function parsePeriod(value:string) {
  const m=value.match(/^(\d{4}-(?:0[1-9]|1[0-2]))\s+—\s*(\d{4}-(?:0[1-9]|1[0-2])|Present)?$/);
  return {start:m?.[1]||'',end:m?.[2]==='Present'?'':m?.[2]||'',current:m?.[2]==='Present',legacy:Boolean(value&&!m)};
}
export default function ExperienceDates({value,onChange,arabic=false}:{value:string;onChange:(value:string)=>void;arabic?:boolean}) {
  const id=useId(); const [draft,setDraft]=useState(()=>parsePeriod(value));
  const [editLegacy,setEditLegacy]=useState(false);
  useEffect(()=>{setDraft(parsePeriod(value));},[value]);
  const invalid=Boolean(draft.start&&draft.end&&!draft.current&&draft.end<draft.start);
  function change(patch:Partial<typeof draft>) {
    const next={...draft,...patch};setDraft(next);
    if(next.legacy&&!next.start)return;
    if(next.start&&next.end&&!next.current&&next.end<next.start)return;
    onChange(next.start ? next.start+' — '+(next.current?'Present':next.end) : '');
  }
  if(draft.legacy&&!editLegacy)return <div className="field"><label htmlFor={id}>{arabic?'الفترة الحالية':'Existing period'}</label><input id={id} value={value} onChange={e=>onChange(e.target.value)}/><small>{arabic?'الفترة القديمة محفوظة دون تغيير.':'Your existing period is preserved exactly.'}</small><button type="button" className="text-btn" onClick={()=>setEditLegacy(true)}>{arabic?'استخدام حقول التاريخ':'Use date fields'}</button></div>;
  return <fieldset className="field" style={{border:0,padding:0,minWidth:0}}><legend>{arabic?'فترة العمل':'Employment dates'}</legend>
    {draft.legacy&&<small>{arabic?'الفترة المحفوظة: ':'Saved period: '}{value}</small>}
    <label htmlFor={id+'-start'}>{arabic?'تاريخ البداية':'Start date'}</label><input id={id+'-start'} type="month" value={draft.start} onChange={e=>change({start:e.target.value})}/>
    <label htmlFor={id+'-end'}>{arabic?'تاريخ النهاية':'End date'}</label><input id={id+'-end'} type="month" value={draft.end} min={draft.start||undefined} disabled={draft.current} aria-invalid={invalid} aria-describedby={invalid?id+'-error':undefined} onChange={e=>change({end:e.target.value})}/>
    <label><input type="checkbox" checked={draft.current} onChange={e=>change({current:e.target.checked})}/>{arabic?'أعمل هنا حاليًا':'Currently working'}</label>
    {invalid&&<small id={id+'-error'} role="alert">{arabic?'تاريخ النهاية يجب ألا يسبق البداية. لم يُطبّق التغيير.':'End date must not precede start date. This change has not been applied.'}</small>}
  </fieldset>;
}
