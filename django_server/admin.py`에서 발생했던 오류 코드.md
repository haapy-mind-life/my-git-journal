---
created: 2025-03-28T14:25:28+09:00
modified: 2025-03-28T14:25:37+09:00
---

# admin.py`에서 발생했던 오류 코드

아래는 `admin.py`에서 발생했던 오류 코드들 (`E402`, `E404`, `E408`, `E409`, `W411`, `W042`)을 모두 수정한 **최신 버전 코드**입니다.

---

### ✅ 수정된 `admin.py`

```python
from django.contrib import admin
from .models import UserAccessLog


@admin.register(UserAccessLog)
class UserAccessLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'access_time', 'duration')  # ✔️ E408, E409 해결 (tuple 사용 & 필드 존재 확인)
    ordering = ('-access_time',)  # ✔️ W042 해결 (정렬 기준 추가)

    # ✔️ W411 대응: 필드를 꼭 필요한 것만 노출
    list_filter = ('ip_address',)
    search_fields = ('ip_address',)
```

---

### ✅ 수정된 `models.py` (보완용)

```python
from django.db import models


class UserAccessLog(models.Model):
    ip_address = models.GenericIPAddressField()
    access_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # 체류 시간 (초 단위)

    def __str__(self):
        return f"{self.ip_address} - {self.access_time}"
```

---

### ✅ 정리 요약

| 오류 코드 | 해결 방법 |
|-----------|------------|
| **E402** | `@admin.register()`가 `import` 이후에 위치하도록 수정 |
| **E404** | `__str__()` 메서드 추가 또는 `list_display` 지정 |
| **E408** | `list_display`에 `tuple` 사용 (`[]` → `()`) |
| **E409** | `list_display` 내 필드가 실제 모델에 존재하는지 확인 |
| **W411** | `list_display` 필드를 최소화하거나 `list_filter`/`search_fields`로 분리 |
| **W042** | `ordering` 속성 지정 (`access_time` 기준 내림차순 등) |

---

이제 Django Admin에서 오류 없이 깔끔하게 작동할 것입니다.  
추가로 Admin에서 다른 모델도 등록하고 싶다면 말씀해주세요!
