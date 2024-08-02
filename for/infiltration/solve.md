# FLAG

**corctf{alw4y5_l3m0n_7h1nk_b3f0r3_y0u_c0mm1t_cr1m3}**

## ANALYSIS

Trước khi vào bài, ta được nhận 1 file log có tên là security log, từ đó có thể dễ dàng nhận ra đây là 1 bài về endpoint forensics hay cụ thể là Event Log Viewer.

Bắt đầu với các câu hỏi mà bài đã cho khi ta connect vào server. Từ đó dựa vào các câu hỏi để làm bài.

## WALKTHROUGH

### 1ST QUESTION

```Hello agent. Thanks for your hard work in the field researching. We'll now ask you 6 questions on the information you've gathered.
I'd like to take this opportunity to remind you that our targets are located in the United Kingdom, so their timezone is BST (UTC +1).
We'd like to confirm what the username of the main user on the target's computer is. Can you provide this information?
```

Với câu hỏi đầu tiên, ta được bảo phải tìm username của main user trên máy tính bị tấn công. Có rất nhiều cách làm điều này, nhưng mình biết được rằng mọi thông tin của 1 user được lưu vào SAM, ví dụ như password, group member, SID, v.v

Vì thế nên mình chỉ cần tìm Task Category là SAM và Event ID của nó là 4656:

![image](https://github.com/user-attachments/assets/a27834f0-3eae-4803-a154-9d9f3e6a25f6)

### 2ND QUESTION

```Now, we'd like the name of the computer, after it was renamed. Ensure that it is entered in exactly how it is in the logs. ```

Lúc này, vẫn ở SAM và vẫn ở chỗ đó, ở trong Windows Event Log sẽ xuất hiện description của Log đó. Khi ta chú ý xuống thì ta sẽ được dòng này

![image](https://github.com/user-attachments/assets/f6bca022-1d9b-4879-80d2-4191cf8560de)

### 3RD QUESTION

``` I wonder if they'll make any lemonade with that lemon-squeezer...
Great work! In order to prevent their lemons from moulding, the lemonthinkers changed the maximum password age. What is this value? Please enter it as an integer number in days.
```

Ở đây thì bài bảo ta phải đi tìm maximum password age. Mình có đọc được bài này của Microsoft để tìm minimum password length

https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/minimum-password-length

Và ở đó có 1 mục tên là Maximum password age nằm trong phần Password Policy 

![image](https://github.com/user-attachments/assets/32587c2d-c808-4ef6-b429-0b5af7c915ab)

Vậy nên mình có thể xác định được nơi muốn tìm ở đây là Windows Policy. Task Category sẽ là Authentication Policy Change và Event ID là 4739.

**Max. Password Age:	83:00:00:00**

### 4TH QUESTION

```It seems that our targets are incredibly smart, and turned off the antivirus. At what time did this happen? Give your answer as a UNIX timestamp. ```

Vậy là lúc này, ta cần phải đi tìm khoảng thời gian mà tên này đã tắt antivirus và chuyển nó sang UNIX timestamp. Lúc này, mình xác định được vị trí để tìm là Windows Defender vì đây là trình antivirus có sẵn trên Windows.

Lúc này, vì đã tìm ra nên mình đơn giản là CTRF + F.

![image](https://github.com/user-attachments/assets/0584aba6-8430-4dbd-9203-313d883c830a)

Vậy là mình đã tìm ra. Giờ thì chỉ việc chuyển nó sang giờ UNIX là được

![image](https://github.com/user-attachments/assets/1d9e32d5-ad4f-48b4-9b16-37e939a47c03)

### 5TH QUESTION

```The main lemonthinker, slice1, hasn't learnt from the-conspiracy and has (again) downloaded some malware on the system. What is the name of the user created by this malware? ```

Ở đây, đề bài yêu cầu mình phải tìm tên của user đã được tạo ra bởi con malware gì đó ở trên máy. Dựa vào cách tìm ở câu 1, mình dễ dàng tìm được câu trả lời cho câu này. Hoặc là mình nghĩ vậy. Nó không hoạt động như mình mong muốn.

Nhưng lúc này mình nhớ ra có 1 task gọi là User Account Management với Event ID là 4720. Lúc này mình thấy audit event này là **A user account was created.** vì vậy nên mình khá chắc nó nằm ở đây

![image](https://github.com/user-attachments/assets/697b8766-5ac5-4698-bbb9-523e8a5e3e9a)

### FINAL QUESTION

``` Finally, we'd like to know the name of the group that the user created by the malware is part of, which has the greatest security risk. What is this?  ```

Lúc này, mình nhớ đến có 1 task để tìm group là Group Membership với Event ID là 4627. Lúc này mình thấy 2 account name là slice1 và notabackdoor đều ở chung 1 group membership.

```Group Membership:			
		S-1-5-21-2883796447-3563202477-3898649884-513
		Everyone
		NT AUTHORITY\Local account and member of Administrators group
		BUILTIN\Administrators
		BUILTIN\Users
		NT AUTHORITY\INTERACTIVE
		CONSOLE LOGON
		NT AUTHORITY\Authenticated Users
		NT AUTHORITY\This Organization
		NT AUTHORITY\Local account
		LOCAL
		NT AUTHORITY\NTLM Authentication
		Mandatory Label\Medium Mandatory Level
```

Đây là 1 số thứ có ở trong và đề bài yêu cầu phải tìm highest risk, ở đây thì mình nhận ra ngay Administrators là group có độ rủi ro về bảo mật nhất.

## Kiến thức thu được

Sau khi cho người anh trong CLB tham khảo bài wu này của mình, anh ý có bổ sung cho mình thêm về một số thứ có ích.

**Password Policy** ví dụ như hành động thay đổi policy hay brute force, password spray với wordlist được chỉnh để né policy chẳng hạn. Sau khi xem thử trên mitre thì mình thấy rằng nó có 1 mitigation liên quan đến.

https://attack.mitre.org/mitigations/M1027/

Tuy nhiên thì không chỉ có mỗi **Password Policy** mà còn là cả về **Group Policy** 

Để giải thích thì: ở trong group policy, kẻ tấn công sẽ có thể thu được thông tin từ Group Policy settings để xác định được đường dẫn giúp ích cho **Privileged Escalation** hay trong tiếng Việt là leo quyền, và khi đã leo quyền lên Admin thành công, thì kẻ tấn công này có thể thao túng hay là nắm quyền kiểm soát cái Group Policy này.

Mitre Attack technique: T1615

https://attack.mitre.org/techniques/T1615/

-> Chốt lại thì theo mình đánh giá đây là 1 bài tương đối dễ và nhập môn của Endpoint Forensics, nhưng cảm ơn tác giả vì đã cho một bài mà mình đã lâu rồi mới được trải nghiệm ở 1 giải CTF 







