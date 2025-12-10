// src/components/OperatorSelect.tsx
import React from "react";
import "../App.css";

interface OperatorSelectProps {
    value: string;
    onChange: (op: string) => void;
}

const OperatorSelect: React.FC<OperatorSelectProps> = ({ value, onChange }) => {
    return (
        <div className="operator-box">
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="operator-select"
            >
                <option value="+">+</option>
                <option value="-">-</option>
                <option value="*">×</option>
                <option value="/">÷</option>
            </select>
        </div>
    );
};

export default OperatorSelect;