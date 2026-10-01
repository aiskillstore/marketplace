// ---------- JsonLogic core (subset covering jsonlogic.com/operations.html) ----------
// Static — never templated, never changes between publishes. Loaded once via
// <script src="jsonlogic-core.js"> by playground.html; only playground.html itself
// gets re-templated and republished when the rule/data/language changes.
"use strict";

function getVar(data, path, defaultVal){
  if(path === "" || path === null || path === undefined) return data;
  var parts = String(path).split(".");
  var cur = data;
  for(var i=0;i<parts.length;i++){
    if(cur === null || cur === undefined) return defaultVal===undefined?null:defaultVal;
    cur = cur[parts[i]];
  }
  return cur===undefined ? (defaultVal===undefined?null:defaultVal) : cur;
}

function jsonLogicTruthy(v, mode){
  if(mode === "ruby"){
    // Ruby: only false and nil are falsy. 0, "", [] are truthy.
    return !(v === false || v === null || v === undefined);
  }
  // default JsonLogic/JS-derived truthy
  if(Array.isArray(v)) return v.length > 0;
  return !!v;
}

function apply(rule, data, mode){
  if(rule === null || typeof rule !== "object" || Array.isArray(rule)){
    return rule;
  }
  var op = Object.keys(rule)[0];
  var vals = rule[op];
  if(!Array.isArray(vals)) vals = [vals];

  function A(i){ return apply(vals[i], data, mode); }
  function AA(){ return vals.map(function(v){ return apply(v, data, mode); }); }

  switch(op){
    case "var": return getVar(data, A(0), vals.length>1?A(1):undefined);
    case "missing": {
      var keys = AA();
      return keys.filter(function(k){ return getVar(data,k,undefined)===null; });
    }
    case "missing_some": {
      var need = A(0);
      var keys2 = apply(vals[1], data, mode);
      var present = keys2.filter(function(k){ return getVar(data,k,undefined)!==null; });
      var missing2 = keys2.filter(function(k){ return getVar(data,k,undefined)===null; });
      return present.length >= need ? [] : missing2;
    }
    case "if": case "?:": {
      var i=0;
      while(i < vals.length - 1){
        if(jsonLogicTruthy(A(i), mode)) return A(i+1);
        i += 2;
      }
      return i < vals.length ? A(i) : null;
    }
    case "==": return A(0) == A(1);
    case "===": return A(0) === A(1);
    case "!=": return A(0) != A(1);
    case "!==": return A(0) !== A(1);
    case ">": return A(0) > A(1);
    case ">=": return A(0) >= A(1);
    case "<": return vals.length===3 ? (A(0) < A(1) && A(1) < A(2)) : A(0) < A(1);
    case "<=": return vals.length===3 ? (A(0) <= A(1) && A(1) <= A(2)) : A(0) <= A(1);
    case "!": return !jsonLogicTruthy(A(0), mode);
    case "!!": return jsonLogicTruthy(A(0), mode);
    case "and": {
      var r; for(var j=0;j<vals.length;j++){ r = A(j); if(!jsonLogicTruthy(r,mode)) return r; } return r;
    }
    case "or": {
      var r2; for(var k=0;k<vals.length;k++){ r2 = A(k); if(jsonLogicTruthy(r2,mode)) return r2; } return r2;
    }
    case "+": return AA().reduce(function(a,b){ return Number(a)+Number(b); },0);
    case "*": return AA().reduce(function(a,b){ return Number(a)*Number(b); },1);
    case "-": { var n=AA(); return n.length===1 ? -n[0] : n.reduce(function(a,b){return a-b;}); }
    case "/": { var n2=AA(); return n2.reduce(function(a,b){return a/b;}); }
    case "%": return A(0) % A(1);
    case "min": return Math.min.apply(null, AA());
    case "max": return Math.max.apply(null, AA());
    case "in": {
      var needle=A(0), hay=A(1);
      if(typeof hay === "string") return hay.indexOf(needle) !== -1;
      if(Array.isArray(hay)) return hay.indexOf(needle) !== -1;
      return false;
    }
    case "cat": return AA().map(function(v){return v===null||v===undefined?"":String(v);}).join("");
    case "substr": {
      var s=A(0), start=A(1), len=vals.length>2?A(2):undefined;
      if(len===undefined) return s.substring(start<0? s.length+start : start);
      if(len<0) return s.substring(start<0? s.length+start:start, s.length+len);
      return s.substr(start, len);
    }
    case "merge": {
      var out=[]; AA().forEach(function(v){ out = out.concat(Array.isArray(v)?v:[v]); }); return out;
    }
    case "map": {
      var arr=A(0)||[]; var sub=vals[1];
      return arr.map(function(item){ return apply(sub, item, mode); });
    }
    case "filter": {
      var arr2=A(0)||[]; var sub2=vals[1];
      return arr2.filter(function(item){ return jsonLogicTruthy(apply(sub2,item,mode), mode); });
    }
    case "reduce": {
      var arr3=A(0)||[]; var sub3=vals[1]; var init=A(2);
      return arr3.reduce(function(acc,cur){ return apply(sub3, {current:cur, accumulator:acc}, mode); }, init);
    }
    case "all": {
      var arr4=A(0)||[]; var sub4=vals[1];
      return arr4.length>0 && arr4.every(function(item){ return jsonLogicTruthy(apply(sub4,item,mode), mode); });
    }
    case "none": {
      var arr5=A(0)||[]; var sub5=vals[1];
      return !arr5.some(function(item){ return jsonLogicTruthy(apply(sub5,item,mode), mode); });
    }
    case "some": {
      var arr6=A(0)||[]; var sub6=vals[1];
      return arr6.some(function(item){ return jsonLogicTruthy(apply(sub6,item,mode), mode); });
    }
    case "log": { var v=A(0); return v; }
    default:
      throw new Error("Unsupported operator: \"" + op + "\"");
  }
}
