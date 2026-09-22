const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1200,height:630},deviceScaleFactor:1});
 const p=await ctx.newPage();
 for(const s of ['home','menu','story','visit','jobs']){
   await p.goto('file:///home/claude/solsite/build/og/og-'+s+'.html',{waitUntil:'domcontentloaded'});
   await p.waitForTimeout(1500);
   await p.screenshot({path:`/home/claude/solsite/build/og/png/og-${s}.png`});
 }
 console.log('og done'); await b.close();
})();
