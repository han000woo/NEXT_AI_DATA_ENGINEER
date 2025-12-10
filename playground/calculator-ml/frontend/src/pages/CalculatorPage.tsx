import { useState } from "react";
import DigitCanvas from "../components/DigitCanvas";
import "../App.css";

// 1. 블록의 타입 정의
type ItemType = "DIGIT" | "OPERATOR" | "PAREN_L" | "PAREN_R" | "SQRT" | "POWER";

interface CalcItem {
  id: number;
  type: ItemType;
  value: string | number; // 숫자는 0~9, 연산자는 "+", 특수기호는 "sqrt" 등
}

const CalculatorPage = () => {
  // 모든 블록을 순서대로 관리하는 하나의 리스트
  const [items, setItems] = useState<CalcItem[]>([
    { id: Date.now(), type: "DIGIT", value: 0 } // 초기값: 숫자칸 1개
  ]);
  const [result, setResult] = useState<string>("");

  // 2. 블록 추가 함수
  const addItem = (type: ItemType, initialValue: string | number = "") => {
    const newItem: CalcItem = {
      id: Date.now(),
      type,
      value: initialValue,
    };
    setItems([...items, newItem]);
  };

  // 3. 블록 삭제 함수
  const removeItem = (id: number) => {
    setItems(items.filter((item) => item.id !== id));
  };

  // 4. 값 업데이트 (숫자 인식 결과 or 연산자 변경)
  const updateItemValue = (id: number, newValue: string | number) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, value: newValue } : item))
    );
  };

  const initItem = () => {
    setItems([{id: Date.now(), type: "DIGIT",value : 0}]);
    setResult("");
  }

  // 5. 계산 로직 (핵심!)
  const calculate = () => {
    let formula = "";
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      // const nextItem = items[i + 1];

      // 값 처리
      if (item.type === "DIGIT") {
        formula += item.value;
        // 다음 아이템도 숫자면 붙여쓰기 (자릿수 추가 효과), 아니면 띄어쓰기 필요 없음
      } else if (item.type === "OPERATOR") {
        formula += ` ${item.value} `;
      } else if (item.type === "PAREN_L") {
        formula += "(";
      } else if (item.type === "PAREN_R") {
        formula += ")";
      } else if (item.type === "POWER") {
        formula += "**"; // JS에서 제곱 연산자
      } else if (item.type === "SQRT") {
        formula += "Math.sqrt("; 
        // 주의: 루트는 여는 괄호를 포함하므로, 사용자가 닫는 괄호를 추가해줘야 정확함
        // UX 개선을 위해 자동으로 닫는 괄호 로직을 넣을 수도 있지만, 
        // 지금은 자유도 높게 사용자가 ')'를 추가하는 방식으로 둡니다.
      }
    }

    try {
      console.log("Calculated Formula:", formula); // 디버깅용
      // eslint-disable-next-line no-eval
      const calcResult = eval(formula);
      
      if (isNaN(calcResult) || !isFinite(calcResult)) {
        setResult("Error");
      } else {
        // 소수점 처리
        setResult(Number.isInteger(calcResult) ? calcResult.toString() : calcResult.toFixed(4));
      }
    } catch (e) {
      setResult("수식 오류");
    }
  };

  return (
    <div className="page-container">
      <h2 className="page-title">자유형 손글씨 계산기</h2>
      <p className="page-desc">
        원하는 블록을 추가하여 자유롭게 수식을 만들어보세요.
      </p>

      {/* 툴바 영역 */}
      <div className="toolbar">
        <button onClick={() => addItem("DIGIT", 0)} className="tool-btn add-digit">
          + ⬜ 숫자칸
        </button>
        <div className="divider"></div>
        <button onClick={() => addItem("OPERATOR", "+")} className="tool-btn">연산자</button>
        <button onClick={() => addItem("PAREN_L", "(")} className="tool-btn">(</button>
        <button onClick={() => addItem("PAREN_R", ")")} className="tool-btn">)</button>
        <button onClick={() => addItem("POWER", "^")} className="tool-btn">x² (제곱)</button>
        <button onClick={() => addItem("SQRT", "sqrt")} className="tool-btn">√ (루트)</button>
        <div className="divider"></div>
        <button onClick={initItem} className="tool-btn reset-btn">
          초기화
        </button>
      </div>

      {/* 수식 입력 영역 (가로 스크롤 가능하게 처리) */}
      <div className="equation-scroll-area">
        <div className="equation-area-flexible">
          {items.map((item) => (
            <div key={item.id} className="block-wrapper fade-in">
              
              {/* 1. 숫자 칸인 경우 */}
              {item.type === "DIGIT" && (
                <DigitCanvas
                  id={item.id}
                  value={item.value}
                  onPredict={updateItemValue}
                  onDelete={removeItem}
                  isRemovable={true}
                />
              )}

              {/* 2. 연산자 블록인 경우 */}
              {item.type === "OPERATOR" && (
                <div className="symbol-block operator">
                  <select
                    value={item.value}
                    onChange={(e) => updateItemValue(item.id, e.target.value)}
                  >
                    <option value="+">+</option>
                    <option value="-">-</option>
                    <option value="*">×</option>
                    <option value="/">÷</option>
                  </select>
                  <button onClick={() => removeItem(item.id)} className="mini-close">×</button>
                </div>
              )}

              {/* 3. 특수 기호 블록들 */}
              {["PAREN_L", "PAREN_R", "POWER", "SQRT"].includes(item.type) && (
                <div className="symbol-block special">
                  <span>
                    {item.type === "PAREN_L" && "("}
                    {item.type === "PAREN_R" && ")"}
                    {item.type === "POWER" && "^"}
                    {item.type === "SQRT" && "√"}
                  </span>
                  <button onClick={() => removeItem(item.id)} className="mini-close">×</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 결과 영역 */}
      <div className="footer-calculate">
        <button onClick={calculate} className="calc-btn">
          = 계산하기
        </button>
        <div className="result-display">
          <span className="result-label">결과:</span> {result}
        </div>
      </div>
    </div>
  );
};

export default CalculatorPage;