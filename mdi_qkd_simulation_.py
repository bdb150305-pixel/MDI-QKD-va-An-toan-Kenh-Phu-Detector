"""
MÔ PHỎNG MONTE CARLO MDI-QKD
============================
Mô hình hệ thống nguyên mẫu: Alice -> Charlie <- Bob

Chương trình mô phỏng:
- Alice và Bob chọn bit ngẫu nhiên và cơ sở đo Z/X.
- Suy hao kênh sợi quang.
- Hiệu suất detector.
- Xác suất dark count (xung tối).
- Mô hình đơn giản hóa cho phép đo trạng thái Bell (BSM).
- Sifting: giữ các lượt có BSM thành công và cùng cơ sở.
- Tính QBER (tỷ lệ lỗi bit lượng tử).
- Tính chỉ số key rate proxy để khảo sát xu hướng.
- Khảo sát khoảng cách, hiệu suất detector và dark count.

Thư viện cần thiết:
    pip install numpy pandas matplotlib

Cách chạy:
    python mdi_qkd_simulation.py

LƯU Ý:
Đây là mô hình nguyên mẫu ở mức hệ thống phục vụ bài tập lớn.
Chương trình chưa phải mô phỏng quang lượng tử đầy đủ, chưa triển khai
ước lượng decoy-state và chưa cung cấp chứng minh bảo mật hữu hạn.
Chỉ số key_rate trong chương trình là chỉ số tham khảo, không phải
tốc độ khóa bí mật đã được chứng minh an toàn.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# CẤU HÌNH MÔ PHỎNG
# =========================

SO_VONG_MO_PHONG = 500_000
SUY_HAO_SOI_DB_MOI_KM = 0.20
HIEU_SUAT_DETECTOR_MAC_DINH = 0.85
DARK_COUNT_MAC_DINH = 1e-6
XAC_SUAT_BSM_THANH_CONG = 0.50
LOI_NOI_TAI_MAC_DINH = 0.01
HE_SO_HIEU_CHINH_LOI = 1.16
SEED_NGAU_NHIEN = 20261008

KHOANG_CACH_KM = np.arange(0, 51, 5)

CAC_HIEU_SUAT_DETECTOR = np.array([
    0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95
])

# Bổ sung các mức dark count cao để khảo sát căng thẳng (stress test).
# Các mức cao này nhằm làm rõ xu hướng trong mô hình, không mặc định
# là thông số thực tế của detector.
CAC_MUC_DARK_COUNT = np.array([
    0.0, 1e-7, 5e-7, 1e-6, 5e-6,
    1e-5, 5e-5, 1e-4, 1e-3, 1e-2
])

KHOANG_CACH_KHAO_SAT_HIEU_SUAT_KM = 20
KHOANG_CACH_KHAO_SAT_DARK_COUNT_KM = 100

# Lưu kết quả trong thư mục "results" nằm cạnh file Python.
THU_MUC_GOC = Path(__file__).resolve().parent
THU_MUC_KET_QUA = THU_MUC_GOC / "results"
THU_MUC_KET_QUA.mkdir(parents=True, exist_ok=True)


def entropy_nhi_phan(q):
    """Tính entropy nhị phân H2(q), với q là xác suất lỗi."""
    q = float(np.clip(q, 0.0, 1.0))

    if q <= 0.0 or q >= 1.0:
        return 0.0

    return -q * np.log2(q) - (1.0 - q) * np.log2(1.0 - q)


def do_truyen_kenh(distance_km, suy_hao_db_moi_km=SUY_HAO_SOI_DB_MOI_KM):
    """
    Tính độ truyền qua một nhánh quang khi Charlie nằm giữa Alice và Bob.

    distance_km: khoảng cách tổng Alice-Bob.
    Mỗi nhánh có độ dài distance_km / 2.
    """
    do_dai_moi_nhanh_km = distance_km / 2.0
    return 10 ** (-(suy_hao_db_moi_km * do_dai_moi_nhanh_km) / 10.0)


def mo_phong_mdi_qkd(
    khoang_cach_km,
    so_vong=SO_VONG_MO_PHONG,
    suy_hao_db_moi_km=SUY_HAO_SOI_DB_MOI_KM,
    hieu_suat_detector=HIEU_SUAT_DETECTOR_MAC_DINH,
    dark_count=DARK_COUNT_MAC_DINH,
    xac_suat_bsm=XAC_SUAT_BSM_THANH_CONG,
    loi_noi_tai=LOI_NOI_TAI_MAC_DINH,
    he_so_hieu_chinh_loi=HE_SO_HIEU_CHINH_LOI,
    rng=None,
):
    """Chạy một thí nghiệm Monte Carlo MDI-QKD ở mức hệ thống."""
    if rng is None:
        rng = np.random.default_rng()

    # Sinh bit ngẫu nhiên của Alice.
    # Trong mô hình lý tưởng đơn giản này, bit ban đầu của Bob tương quan
    # với bit Alice; lỗi được đưa vào ở bước mô hình hóa lỗi phía dưới.
    bit_alice = rng.integers(0, 2, so_vong)
    bit_bob = bit_alice.copy()

    # Chọn cơ sở BB84: 0 tương ứng Z, 1 tương ứng X.
    co_so_alice = rng.integers(0, 2, so_vong)
    co_so_bob = rng.integers(0, 2, so_vong)
    cung_co_so = co_so_alice == co_so_bob

    # Mỗi nhánh quang dài một nửa khoảng cách tổng.
    do_truyen = do_truyen_kenh(khoang_cach_km, suy_hao_db_moi_km)
    xac_suat_phat_hien_tin_hieu = do_truyen * hieu_suat_detector

    # Mô phỏng phát hiện tín hiệu và dark count độc lập trên mỗi nhánh.
    phat_hien_tin_hieu_alice = (
        rng.random(so_vong) < xac_suat_phat_hien_tin_hieu
    )
    phat_hien_tin_hieu_bob = (
        rng.random(so_vong) < xac_suat_phat_hien_tin_hieu
    )

    dark_alice = rng.random(so_vong) < dark_count
    dark_bob = rng.random(so_vong) < dark_count

    # Detector ghi nhận phát hiện nếu có tín hiệu hoặc dark count.
    phat_hien_alice = phat_hien_tin_hieu_alice | dark_alice
    phat_hien_bob = phat_hien_tin_hieu_bob | dark_bob

    # Mô hình BSM đơn giản:
    # BSM chỉ có thể thành công khi cả hai nhánh đều có phát hiện,
    # sau đó lấy mẫu theo xác suất thành công BSM đã cho.
    su_kien_bsm = (
        phat_hien_alice
        & phat_hien_bob
        & (rng.random(so_vong) < xac_suat_bsm)
    )

    # Sifting: chỉ giữ các lượt BSM thành công và hai bên chọn cùng cơ sở.
    bit_duoc_giu = su_kien_bsm & cung_co_so
    so_bit_duoc_giu = int(bit_duoc_giu.sum())

    # Số sự kiện có cả hai nhánh phát hiện tín hiệu, trước điều kiện BSM/sifting.
    su_kien_cap_tin_hieu = (
        phat_hien_tin_hieu_alice & phat_hien_tin_hieu_bob
    )

    if so_bit_duoc_giu == 0:
        return {
            "khoang_cach_km": khoang_cach_km,
            "suy_hao_tong_db": suy_hao_db_moi_km * khoang_cach_km,
            "do_dai_moi_nhanh_km": khoang_cach_km / 2.0,
            "do_truyen_kenh": do_truyen,
            "hieu_suat_detector": hieu_suat_detector,
            "dark_count": dark_count,
            "xac_suat_bsm": xac_suat_bsm,
            "so_vong": so_vong,
            "so_su_kien_bsm": int(su_kien_bsm.sum()),
            "so_bit_duoc_giu": 0,
            "so_bit_loi": 0,
            "qber": np.nan,
            "ty_le_bit_duoc_giu": 0.0,
            "key_rate_proxy": 0.0,
        }

    # Phân loại nguồn phát hiện theo mô hình đơn giản.
    # Nếu cả hai nhánh đều có phát hiện tín hiệu, dùng xác suất lỗi nội tại.
    # Nếu không, sự kiện được mô hình hóa là có đóng góp dark count và
    # bit có xác suất sai 50%.
    #
    # Đây là giả định của mô hình nguyên mẫu; detector thực tế không thể
    # luôn xác định nguồn gốc sự kiện chỉ từ một cờ phát hiện nhị phân.
    cap_phat_hien_tin_hieu = (
        phat_hien_tin_hieu_alice & phat_hien_tin_hieu_bob
    )

    xac_suat_loi_hieu_dung = np.where(
        cap_phat_hien_tin_hieu,
        loi_noi_tai,
        0.5,
    )

    su_kien_loi = rng.random(so_vong) < xac_suat_loi_hieu_dung

    bit_bob_quan_sat = bit_bob.copy()
    bit_bob_quan_sat[su_kien_loi] ^= 1

    so_bit_loi = int(
        np.sum(bit_alice[bit_duoc_giu] != bit_bob_quan_sat[bit_duoc_giu])
    )
    qber = so_bit_loi / so_bit_duoc_giu
    ty_le_bit_duoc_giu = so_bit_duoc_giu / so_vong

    # Chỉ số key rate proxy đơn giản để khảo sát xu hướng.
    # Không phải công thức tốc độ khóa bí mật đầy đủ của MDI-QKD.
    entropy_loi = entropy_nhi_phan(qber)
    key_rate_proxy = ty_le_bit_duoc_giu * max(
        0.0,
        1.0 - he_so_hieu_chinh_loi * entropy_loi - entropy_loi,
    )

    return {
        "khoang_cach_km": khoang_cach_km,
        "suy_hao_tong_db": suy_hao_db_moi_km * khoang_cach_km,
        "do_dai_moi_nhanh_km": khoang_cach_km / 2.0,
        "do_truyen_kenh": do_truyen,
        "hieu_suat_detector": hieu_suat_detector,
        "dark_count": dark_count,
        "xac_suat_bsm": xac_suat_bsm,
        "so_vong": so_vong,
        "so_su_kien_bsm": int(su_kien_bsm.sum()),
        "so_bit_duoc_giu": so_bit_duoc_giu,
        "so_bit_loi": so_bit_loi,
        "qber": qber,
        "ty_le_bit_duoc_giu": ty_le_bit_duoc_giu,
        "key_rate_proxy": key_rate_proxy,
    }


def khao_sat_khoang_cach(rng):
    """Khảo sát ảnh hưởng của khoảng cách Alice-Bob."""
    ket_qua = []
    print("[1/3] Đang khảo sát khoảng cách...")

    for khoang_cach in KHOANG_CACH_KM:
        ket_qua.append(mo_phong_mdi_qkd(
            float(khoang_cach),
            hieu_suat_detector=HIEU_SUAT_DETECTOR_MAC_DINH,
            dark_count=DARK_COUNT_MAC_DINH,
            rng=rng,
        ))

    bang = pd.DataFrame(ket_qua)
    bang.to_csv(
        THU_MUC_KET_QUA / "mdiqkd_distance_results.csv",
        index=False,
    )
    return bang


def khao_sat_hieu_suat_detector(rng):
    """Khảo sát ảnh hưởng của hiệu suất detector."""
    ket_qua = []
    print("[2/3] Đang khảo sát hiệu suất detector...")

    for hieu_suat in CAC_HIEU_SUAT_DETECTOR:
        ket_qua.append(mo_phong_mdi_qkd(
            KHOANG_CACH_KHAO_SAT_HIEU_SUAT_KM,
            hieu_suat_detector=float(hieu_suat),
            dark_count=DARK_COUNT_MAC_DINH,
            rng=rng,
        ))

    bang = pd.DataFrame(ket_qua)
    bang.to_csv(
        THU_MUC_KET_QUA / "mdiqkd_detector_efficiency_results.csv",
        index=False,
    )
    return bang


def khao_sat_dark_count(rng):
    """Khảo sát ảnh hưởng của dark count ở khoảng cách được chỉ định."""
    ket_qua = []
    print("[3/3] Đang khảo sát dark count...")

    for dark_count in CAC_MUC_DARK_COUNT:
        ket_qua.append(mo_phong_mdi_qkd(
            KHOANG_CACH_KHAO_SAT_DARK_COUNT_KM,
            hieu_suat_detector=HIEU_SUAT_DETECTOR_MAC_DINH,
            dark_count=float(dark_count),
            rng=rng,
        ))

    bang = pd.DataFrame(ket_qua)
    bang.to_csv(
        THU_MUC_KET_QUA / "mdiqkd_dark_count_results.csv",
        index=False,
    )
    return bang


def luu_bieu_do(
    ten_file,
    truc_x,
    truc_y,
    nhan_truc_x,
    nhan_truc_y,
    tieu_de,
    truc_x_log=False,
):
    """Vẽ và lưu một biểu đồ PNG."""
    plt.figure(figsize=(8, 5))

    if truc_x_log:
        truc_x = np.asarray(truc_x, dtype=float)
        # Trục log không biểu diễn được số 0; thay 0 bằng giá trị nhỏ
        # chỉ để hiển thị, không thay đổi giá trị trong CSV.
        truc_x_hien_thi = np.where(truc_x == 0, 1e-12, truc_x)
        plt.semilogx(truc_x_hien_thi, truc_y, marker="o")
    else:
        plt.plot(truc_x, truc_y, marker="o")

    plt.xlabel(nhan_truc_x)
    plt.ylabel(nhan_truc_y)
    plt.title(tieu_de)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(THU_MUC_KET_QUA / ten_file, dpi=300, bbox_inches="tight")
    plt.close()


def tao_bieu_do(bang_khoang_cach, bang_hieu_suat, bang_dark_count):
    """Tạo các biểu đồ phục vụ phân tích kết quả."""
    luu_bieu_do(
        "qber_vs_distance.png",
        bang_khoang_cach["khoang_cach_km"],
        bang_khoang_cach["qber"],
        "Khoảng cách Alice-Bob (km)",
        "QBER",
        "Mô hình MDI-QKD: QBER theo khoảng cách",
    )

    luu_bieu_do(
        "key_rate_proxy_vs_distance.png",
        bang_khoang_cach["khoang_cach_km"],
        bang_khoang_cach["key_rate_proxy"],
        "Khoảng cách Alice-Bob (km)",
        "Key rate proxy",
        "Mô hình MDI-QKD: chỉ số key rate proxy theo khoảng cách",
    )

    luu_bieu_do(
        "qber_vs_dark_count.png",
        bang_dark_count["dark_count"],
        bang_dark_count["qber"],
        "Xác suất dark count",
        "QBER",
        f"QBER theo dark count tại {KHOANG_CACH_KHAO_SAT_DARK_COUNT_KM} km",
        truc_x_log=True,
    )

    luu_bieu_do(
        "key_rate_proxy_vs_dark_count.png",
        bang_dark_count["dark_count"],
        bang_dark_count["key_rate_proxy"],
        "Xác suất dark count",
        "Key rate proxy",
        f"Key rate proxy theo dark count tại {KHOANG_CACH_KHAO_SAT_DARK_COUNT_KM} km",
        truc_x_log=True,
    )

    luu_bieu_do(
        "key_rate_proxy_vs_detector_efficiency.png",
        bang_hieu_suat["hieu_suat_detector"],
        bang_hieu_suat["key_rate_proxy"],
        "Hiệu suất detector",
        "Key rate proxy",
        "Key rate proxy theo hiệu suất detector",
    )


def in_ket_qua(bang_khoang_cach, bang_hieu_suat, bang_dark_count):
    """In các bảng kết quả quan trọng ra Terminal."""
    print("\n===== KẾT QUẢ THEO KHOẢNG CÁCH =====")
    print(bang_khoang_cach[[
        "khoang_cach_km",
        "suy_hao_tong_db",
        "so_su_kien_bsm",
        "so_bit_duoc_giu",
        "so_bit_loi",
        "qber",
        "key_rate_proxy",
    ]].to_string(index=False, formatters={
        "qber": lambda x: f"{x:.6f}",
        "key_rate_proxy": lambda x: f"{x:.6f}",
    }))

    print("\n===== KẾT QUẢ THEO HIỆU SUẤT DETECTOR =====")
    print(bang_hieu_suat[[
        "hieu_suat_detector",
        "so_bit_duoc_giu",
        "qber",
        "key_rate_proxy",
    ]].to_string(index=False, formatters={
        "hieu_suat_detector": lambda x: f"{x:.2%}",
        "qber": lambda x: f"{x:.6f}",
        "key_rate_proxy": lambda x: f"{x:.6f}",
    }))

    print("\n===== KẾT QUẢ THEO DARK COUNT =====")
    print(bang_dark_count[[
        "dark_count",
        "so_bit_duoc_giu",
        "so_bit_loi",
        "qber",
        "key_rate_proxy",
    ]].to_string(index=False, formatters={
        "dark_count": lambda x: f"{x:.2e}",
        "qber": lambda x: f"{x:.6f}",
        "key_rate_proxy": lambda x: f"{x:.6f}",
    }))


def main():
    """Hàm chính điều phối các khảo sát và lưu kết quả."""
    print("=" * 65)
    print("MÔ PHỎNG MONTE CARLO MDI-QKD")
    print("=" * 65)
    print(f"Số vòng mô phỏng             : {SO_VONG_MO_PHONG:,}")
    print(f"Suy hao sợi quang             : {SUY_HAO_SOI_DB_MOI_KM} dB/km")
    print(f"Hiệu suất detector mặc định   : {HIEU_SUAT_DETECTOR_MAC_DINH:.0%}")
    print(f"Dark count mặc định           : {DARK_COUNT_MAC_DINH:.1e}")
    print(f"Xác suất BSM thành công       : {XAC_SUAT_BSM_THANH_CONG:.0%}")
    print(f"Lỗi nội tại                   : {LOI_NOI_TAI_MAC_DINH:.2%}")
    print(f"Seed ngẫu nhiên                : {SEED_NGAU_NHIEN}")
    print(f"Thư mục lưu kết quả           : {THU_MUC_KET_QUA}")

    rng = np.random.default_rng(SEED_NGAU_NHIEN)

    bang_khoang_cach = khao_sat_khoang_cach(rng)
    bang_hieu_suat = khao_sat_hieu_suat_detector(rng)
    bang_dark_count = khao_sat_dark_count(rng)

    tao_bieu_do(bang_khoang_cach, bang_hieu_suat, bang_dark_count)
    in_ket_qua(bang_khoang_cach, bang_hieu_suat, bang_dark_count)

    print("\nĐã hoàn thành mô phỏng.")
    print(f"Các file CSV và PNG được lưu tại:\n{THU_MUC_KET_QUA.resolve()}")
    print(
        "\nLưu ý: key_rate_proxy chỉ là chỉ số mô phỏng đơn giản, "
        "không phải tốc độ khóa bí mật được chứng minh an toàn."
    )


if __name__ == "__main__":
    main()
