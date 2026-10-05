from abc import ABC, abstractmethod
from typing import List, Optional, overload

class Employee(ABC):
    #Nạp chồng Constructor
    @overload
    def __init__(self, employee_id: str, full_name: str) -> None: ...
    @overload
    def __init__(self, employee_id: str, full_name: str, department: str) -> None: ...
    
    def __init__(self, *args):
        if len(args) == 2:
            employee_id, full_name = args
            department = "Unassigned"
        elif len(args) == 3:
            employee_id, full_name, department = args
        else:
            raise ValueError("Constructor yêu cầu 2 hoặc 3 tham số.")

        if not employee_id.strip():
            raise ValueError("Mã nhân sự không rỗng.")
        if not full_name.strip():
            raise ValueError("Họ tên không rỗng.")
        if not department.strip():
            raise ValueError("Phòng ban không rỗng.")

        self._employee_id = employee_id
        self._full_name = full_name
        self._department = department
        self._monthly_bonus = 0.0
        
        self._bonus_history = [] 

    @property
    def employee_id(self) -> str: return self._employee_id
    @property
    def full_name(self) -> str: return self._full_name
    @property
    def department(self) -> str: return self._department
    @property
    def monthly_bonus(self) -> float: return self._monthly_bonus

    #Nạp chồng phương thức thưởng
    @overload
    def add_bonus(self, amount: float) -> None: ...
    @overload
    def add_bonus(self, amount: float, reason: str) -> None: ...
    @overload
    def add_bonus(self, rate: float, reference_amount: float, reason: str) -> None: ...

    def add_bonus(self, *args):
        amount = 0.0
        reason = "Không có lý do"

        if len(args) == 1:
            amount = args[0]
            if amount <= 0: raise ValueError("Khoản thưởng phải lớn hơn 0.")
        
        elif len(args) == 2:
            amount, reason = args
            if amount <= 0: raise ValueError("Khoản thưởng phải lớn hơn 0.")
            if not reason.strip(): raise ValueError("Nội dung lý do không được rỗng.")
            
        elif len(args) == 3:
            rate, reference_amount, reason = args
            if not (0 < rate <= 0.5): raise ValueError("Tỷ lệ thưởng phải > 0 và <= 0.5.")
            if reference_amount <= 0: raise ValueError("Giá trị tham chiếu phải > 0.")
            if not reason.strip(): raise ValueError("Nội dung lý do không được rỗng.")
            amount = rate * reference_amount
        else:
            raise ValueError("Số lượng tham số không hợp lệ")

        self._monthly_bonus += amount
        self._bonus_history.append({"amount": amount, "reason": reason})

    @abstractmethod
    def calculate_gross_pay(self) -> float: pass
    
    @abstractmethod
    def get_employee_type(self) -> str: pass

    def display_payroll_info(self) -> str:
        return f"[{self.get_employee_type()}] {self.employee_id} - {self.full_name} | {self.department} | Thưởng: {self.monthly_bonus:,.0f} | Thu nhập: {self.calculate_gross_pay():,.0f}"

class SalariedEmployee(Employee):
    def __init__(self, employee_id: str, full_name: str, department: str, monthly_salary: float, responsibility_allowance: float):
        super().__init__(employee_id, full_name, department)
        if monthly_salary < 0 or responsibility_allowance < 0:
            raise ValueError("Lương và phụ cấp không được âm.")
        self.monthly_salary = monthly_salary
        self.responsibility_allowance = responsibility_allowance

    def calculate_gross_pay(self) -> float:
        return self.monthly_salary + self.responsibility_allowance + self.monthly_bonus

    def get_employee_type(self) -> str:
        return "Salaried"

class HourlyEmployee(Employee):
    def __init__(self, employee_id: str, full_name: str, department: str, hourly_rate: float, worked_hours: float):
        super().__init__(employee_id, full_name, department)
        if hourly_rate < 0:
            raise ValueError("Đơn giá giờ không được âm.")
        if not (0 <= worked_hours <= 250):
            raise ValueError("Số giờ làm hợp lệ từ 0 đến 250.")
        self.hourly_rate = hourly_rate
        self.worked_hours = worked_hours

    def calculate_gross_pay(self) -> float:
        if self.worked_hours <= 160:
            base_pay = self.worked_hours * self.hourly_rate
        else:
            base_pay = 160 * self.hourly_rate + (self.worked_hours - 160) * self.hourly_rate * 1.5
        return base_pay + self.monthly_bonus

    def get_employee_type(self) -> str:
        return "Hourly"

class SalesEmployee(Employee):
    def __init__(self, employee_id: str, full_name: str, department: str, base_salary: float, sales_revenue: float, commission_rate: float):
        super().__init__(employee_id, full_name, department)
        if base_salary < 0 or sales_revenue < 0:
            raise ValueError("Lương cơ bản và doanh số không được âm.")
        if not (0 <= commission_rate <= 0.3):
            raise ValueError("Tỷ lệ hoa hồng nằm trong khoảng từ 0 đến 0.3.")
        self.base_salary = base_salary
        self.sales_revenue = sales_revenue
        self.commission_rate = commission_rate

    def calculate_gross_pay(self) -> float:
        return self.base_salary + (self.sales_revenue * self.commission_rate) + self.monthly_bonus

    def get_employee_type(self) -> str:
        return "Sales"

class Payroll:
    def __init__(self, period: str):
        self.period = period
        self.employee_list: List[Employee] = []

    def add_employee(self, employee: Employee):
        if self.find_employee(employee.employee_id):
            raise ValueError(f"Nhân sự mã {employee.employee_id} đã tồn tại trong bảng lương.")
        self.employee_list.append(employee)

    def find_employee(self, employee_id: str) -> Optional[Employee]:
        for emp in self.employee_list:
            if emp.employee_id == employee_id:
                return emp
        return None

    def calculate_total_payroll(self) -> float:
        return sum(emp.calculate_gross_pay() for emp in self.employee_list)

    def calculate_payroll_by_department(self, department: str) -> float:
        return sum(emp.calculate_gross_pay() for emp in self.employee_list if emp.department == department)

    def find_highest_paid_employee(self) -> Optional[Employee]:
        if not self.employee_list:
            return None
        return max(self.employee_list, key=lambda emp: emp.calculate_gross_pay())

    def display_payroll(self):
        print(f"--- BẢNG LƯƠNG KỲ: {self.period} ---")
        if not self.employee_list:
            print("Danh sách rỗng.")
            return
        for emp in self.employee_list:
            print(emp.display_payroll_info())
        print("-" * 50)
        print(f"Tổng quỹ lương: {self.calculate_total_payroll():,.0f}")

#Kiểm thử
if __name__ == "__main__":
    payroll = Payroll("2026-09")

    # 1. Nhân viên lương cố định
    e1 = SalariedEmployee("E001", "Nguyễn Minh An", "Đào tạo", 15000000, 2000000)
    e1.add_bonus(1000000) # Gọi addBonus(amount)
    payroll.add_employee(e1)

    # 2. Nhân viên theo giờ (<= 160h)
    e2 = HourlyEmployee("E002", "Trần Thu Bình", "Hỗ trợ", 100000, 150)
    e2.add_bonus(500000, "Hoàn thành nhiệm vụ xuất sắc") # Gọi addBonus(amount, reason)
    payroll.add_employee(e2)

    # 3. Nhân viên theo giờ (> 160h)
    e3 = HourlyEmployee("E003", "Lê Hoàng Chi", "Hỗ trợ", 100000, 170)
    # Không có thưởng
    payroll.add_employee(e3)

    # 4. Nhân viên kinh doanh
    e4 = SalesEmployee("E004", "Phạm Quốc Dũng", "Kinh doanh", 8000000, 200000000, 0.05)
    e4.add_bonus(0.02, 50000000, "Đạt mốc doanh thu phụ") # Gọi addBonus(rate, referenceAmount, reason)
    payroll.add_employee(e4)
    
    payroll.display_payroll()
    print(f"Tổng của phòng Hỗ trợ: {payroll.calculate_payroll_by_department('Hỗ trợ'):,.0f}")
    
    highest = payroll.find_highest_paid_employee()
    if highest:
        print(f"Nhân viên lương cao nhất: {highest.full_name} ({highest.calculate_gross_pay():,.0f})")