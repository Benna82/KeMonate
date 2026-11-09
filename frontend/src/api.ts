export type Story={id:number;title:string;creator:string;country:string;region:string;language:string;category:string;source_text:string;translation:string;drafts:Record<string,string>;consent:boolean;ai_consent:boolean;restrictions:string;reviewed:boolean;status:'draft'|'published';media_url:string;media_type:string;updated_at:string;owner:string};
export async function api<T>(path:string, method='GET',data?:unknown):Promise<T>{
 const token=document.cookie.split('; ').find(c=>c.startsWith('csrftoken='))?.split('=')[1]||'';
 const form=data instanceof FormData;
 const r=await fetch('/api/'+path,{method,credentials:'same-origin',headers:{...(method!=='GET'?{'X-CSRFToken':token}:{}),...(!form&&data?{'Content-Type':'application/json'}:{})},body:data?(form?data:JSON.stringify(data)):undefined});
 const type=r.headers.get('content-type');
 if(!type?.includes('application/json'))throw new Error(r.status===403?'Your session has expired. Refresh the page and sign in again.':'The server could not complete this request. Please try again.');
 const result=await r.json(); if(!r.ok)throw new Error(result.error||'Something went wrong. Please try again.'); return result;
}
