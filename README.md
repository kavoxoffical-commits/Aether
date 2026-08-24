# Aether — Weird Facts Shorts Automation

نظام شبه آلي لإنتاج ونشر Weird Facts Shorts على YouTube.

## البنية
- `src/research/` — اكتشاف والتحقق من الحقائق (Research + Verification)
- `src/script/` — كتابة الـ Hook والسكربت
- `src/voice/` — توليد الـ Voiceover
- `src/visuals/` — تجهيز الصور/الفيديوهات
- `src/render/` — دمج الفيديو النهائي
- `src/upload/` — رفع ونشر على YouTube
- `src/storage/` — إدارة الملفات (Drive/محلي مبدئيًا)
- `data/facts/` — الحقائق المكتشفة (raw + verified)
- `data/tracking/` — قاعدة بيانات التتبع (facts.json, videos.json)

## القاعدة الأساسية
- ممنوع الموسيقى الخلفية — SFX فقط عند الحاجة
- لا اختلاق حقائق — كل Fact لازم يمر بـ Research → Verification
- منع التكرار عبر data/tracking/facts.json
- الفيديو ما يظهر أبدًا كأنه AI (تنويع Hooks، أصوات، انتقالات)

## الحالة الحالية
مرحلة البناء الأولى: Research + Verification module.
