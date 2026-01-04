# controllers/service_usage_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.core.database import get_db
from app.models.service_usage import ServiceUsage
from app.models.booking import Booking
from app.models.service import Service
from app.schemas.service_usage import ServiceUsageCreate, ServiceUsageUpdate, ServiceUsageResponse

router = APIRouter()

@router.post("/", 
             response_model=ServiceUsageResponse, 
             status_code=status.HTTP_201_CREATED,
             summary="Tạo mới sử dụng dịch vụ",
             description="Thêm dịch vụ vào booking đã có")
async def create_service_usage(
    service_usage: ServiceUsageCreate,
    db: Session = Depends(get_db)
):
    """
    Tạo mới bản ghi sử dụng dịch vụ cho một booking
    
    - **MaDatPhong**: Mã booking (required)
    - **MaDV**: Mã dịch vụ (required)
    - **SoLuong**: Số lượng (default: 1)
    - **ThanhTien**: Tự động tính nếu không cung cấp
    """
    # Kiểm tra booking tồn tại
    booking = db.query(Booking).filter(Booking.MaDatPhong == service_usage.MaDatPhong).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy booking với ID={service_usage.MaDatPhong}"
        )
    
    # Kiểm tra dịch vụ tồn tại
    service = db.query(Service).filter(Service.MaDV == service_usage.MaDV).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy dịch vụ với ID={service_usage.MaDV}"
        )
    
    # Tính tiền nếu không nhập
    thanh_tien = service_usage.ThanhTien
    if thanh_tien is None:
        # Lấy giá từ bảng DICH_VU (giả sử có field GiaDV)
        thanh_tien = Decimal(str(service.GiaDV)) * service_usage.SoLuong
    
    # Tạo bản ghi mới
    db_item = ServiceUsage(
        MaDatPhong=service_usage.MaDatPhong,
        MaDV=service_usage.MaDV,
        SoLuong=service_usage.SoLuong,
        ThanhTien=thanh_tien
    )
    
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo sử dụng dịch vụ: {str(e)}"
        )

@router.get("/booking/{booking_id}", 
            response_model=List[ServiceUsageResponse],
            summary="Lấy dịch vụ theo booking",
            description="Lấy tất cả dịch vụ đã sử dụng của một booking")
async def get_service_usages_by_booking(
    booking_id: int, 
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách dịch vụ sử dụng theo booking ID
    """
    # Kiểm tra booking tồn tại
    booking = db.query(Booking).filter(Booking.MaDatPhong == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy booking với ID={booking_id}"
        )
    
    items = db.query(ServiceUsage).filter(ServiceUsage.MaDatPhong == booking_id).all()
    return items

@router.get("/{ma_su_dung}", 
            response_model=ServiceUsageResponse,
            summary="Lấy chi tiết sử dụng dịch vụ",
            description="Lấy thông tin chi tiết một bản ghi sử dụng dịch vụ")
async def get_service_usage(
    ma_su_dung: int, 
    db: Session = Depends(get_db)
):
    item = db.query(ServiceUsage).filter(ServiceUsage.MaSuDung == ma_su_dung).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi sử dụng dịch vụ với ID={ma_su_dung}"
        )
    return item

@router.put("/{ma_su_dung}", 
            response_model=ServiceUsageResponse,
            summary="Cập nhật sử dụng dịch vụ",
            description="Cập nhật thông tin sử dụng dịch vụ")
async def update_service_usage(
    ma_su_dung: int,
    service_update: ServiceUsageUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(ServiceUsage).filter(ServiceUsage.MaSuDung == ma_su_dung).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi sử dụng dịch vụ với ID={ma_su_dung}"
        )
    
    # Cập nhật chỉ các field được cung cấp
    update_data = service_update.dict(exclude_unset=True)
    
    # Nếu cập nhật số lượng, tính lại thành tiền
    if 'SoLuong' in update_data and 'ThanhTien' not in update_data:
        service = db.query(Service).filter(Service.MaDV == item.MaDV).first()
        if service:
            update_data['ThanhTien'] = Decimal(str(service.GiaDV)) * update_data['SoLuong']
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    try:
        db.commit()
        db.refresh(item)
        return item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cập nhật: {str(e)}"
        )

@router.delete("/{ma_su_dung}", 
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Xóa sử dụng dịch vụ",
               description="Xóa bản ghi sử dụng dịch vụ")
async def delete_service_usage(
    ma_su_dung: int, 
    db: Session = Depends(get_db)
):
    item = db.query(ServiceUsage).filter(ServiceUsage.MaSuDung == ma_su_dung).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bản ghi sử dụng dịch vụ với ID={ma_su_dung}"
        )
    
    try:
        db.delete(item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa: {str(e)}"
        )
