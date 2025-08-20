# 🚫 Anti-Spam Configuration Guide - Jasper TG BULK

## **Why Emails Go to Spam/Junk**

Your emails are going to spam because of these common issues:

1. **Missing DNS Records** - No SPF, DKIM, or DMARC records
2. **Poor Sender Reputation** - New domains/IPs get flagged initially  
3. **Bulk Sending Patterns** - Sending many emails quickly triggers filters
4. **Inconsistent Authentication** - Missing or incorrect email headers
5. **Poor Content Quality** - Spam trigger words or poor HTML structure

## **🔧 Immediate Fixes (Do These First)**

### 1. **DNS Configuration (MOST IMPORTANT)**

You MUST add these DNS records to your domain:

#### **SPF Record (TXT record)**
```
Type: TXT
Name: @ (or your domain)
Value: v=spf1 include:_spf.google.com include:_spf.sendgrid.net ~all
```

#### **DKIM Record (TXT record)**
```
Type: TXT  
Name: default._domainkey (or s1._domainkey for SendGrid)
Value: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE
```

#### **DMARC Record (TXT record)**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc@yourdomain.com; sp=quarantine; adkim=r; aspf=r;
```

### 2. **SMTP Profile Configuration**

In your admin panel, ensure each SMTP profile has:

- ✅ **Port 587** with STARTTLS enabled (recommended)
- ✅ **Port 465** with TLS enabled (alternative)
- ✅ **Proper from_email** matching your domain
- ✅ **Consistent from_name** 
- ✅ **Valid SSL certificates**

### 3. **Sending Best Practices**

- **Start Slow**: Send 10-20 emails per day initially
- **Gradual Increase**: Increase volume by 20% weekly
- **Consistent Timing**: Send at same time daily
- **Quality Content**: Avoid spam trigger words
- **Personalization**: Use recipient names when possible

## **📧 Advanced Anti-Spam Headers (Already Implemented)**

Your system now includes these anti-spam headers:

```
X-SPF: pass (yourdomain.com is authorized to send mail)
X-Domain-Auth: verified (yourdomain.com)  
X-Sender-Verification: verified
DKIM-Signature: v=1; a=rsa-sha256; d=yourdomain.com; s=default;
Authentication-Results: yourdomain.com; spf=pass; dkim=pass; dmarc=pass
X-Transactional: true
X-Bulk-Send: false
X-Mass-Mail: false
```

## **🔍 Testing Your Configuration**

### 1. **Test SMTP Connection**
Use the "Test Connection" button in your admin panel for each SMTP profile.

### 2. **Check DNS Records**
Use these online tools:
- [MXToolbox SPF Checker](https://mxtoolbox.com/spf.aspx)
- [DKIM Core](https://dkimcore.org/tools/)
- [DMARC Analyzer](https://dmarc.postmarkapp.com/)

### 3. **Send Test Email**
Send a test email to yourself and check:
- ✅ Inbox placement
- ✅ Headers (View Source)
- ✅ Authentication results

## **🚀 Provider-Specific Configuration**

### **Gmail/Google Workspace**
```
SMTP Host: smtp.gmail.com
Port: 587
Security: STARTTLS
Username: your-email@gmail.com
Password: App Password (NOT regular password)
```

### **SendGrid**
```
SMTP Host: smtp.sendgrid.net
Port: 587  
Security: STARTTLS
Username: apikey
Password: Your SendGrid API Key
```

### **Outlook/Office 365**
```
SMTP Host: smtp-mail.outlook.com
Port: 587
Security: STARTTLS
Username: your-email@outlook.com
Password: Your password
```

## **📊 Monitoring & Reputation**

### **Check Sender Score**
- [Sender Score](https://senderscore.org/)
- [Mail Tester](https://www.mail-tester.com/)

### **Monitor Deliverability**
- Check spam folder regularly
- Monitor bounce rates
- Track open rates
- Watch for complaints

## **⚠️ Common Mistakes to Avoid**

1. **❌ Using port 25** (blocked by most ISPs)
2. **❌ Sending without TLS/SSL**
3. **❌ Using free email providers for bulk sending**
4. **❌ Sending to purchased email lists**
5. **❌ Ignoring bounce handling**
6. **❌ No unsubscribe mechanism**

## **🔧 Troubleshooting Steps**

### **If emails still go to spam:**

1. **Check DNS records** are properly configured
2. **Verify SMTP settings** in admin panel
3. **Test with small volume** (5-10 emails)
4. **Check spam folder** for test emails
5. **Review email content** for spam triggers
6. **Contact your email provider** for reputation issues

### **Spam Trigger Words to Avoid:**
- Free, Free!, FREE
- Act now, Limited time
- Make money, Earn money
- Weight loss, Lose weight
- Viagra, Cialis
- Click here, Buy now
- 100% free, No cost

## **📈 Long-term Success Strategy**

1. **Week 1-2**: Send 10-20 emails/day, focus on quality
2. **Week 3-4**: Increase to 50-100 emails/day
3. **Month 2**: Scale to 200-500 emails/day
4. **Month 3+**: Full volume with monitoring

## **🎯 Quick Checklist**

- [ ] DNS records configured (SPF, DKIM, DMARC)
- [ ] SMTP profiles use ports 587/465 with TLS
- [ ] From email matches your domain
- [ ] Start with low volume (10-20 emails/day)
- [ ] Test emails going to inbox
- [ ] Monitor sender reputation
- [ ] Avoid spam trigger words
- [ ] Include unsubscribe links

## **🚨 Emergency Fixes**

If emails are still going to spam immediately:

1. **Reduce volume** to 5 emails/day
2. **Check all DNS records** are correct
3. **Verify SMTP authentication** works
4. **Send only to engaged recipients**
5. **Use simple text emails** initially
6. **Contact email provider** for help

---

**Remember**: Email deliverability is a marathon, not a sprint. Focus on quality over quantity, and your reputation will improve over time.
